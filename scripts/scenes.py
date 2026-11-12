"""Live world-map overlays and palette/pose-triggered radio portraits."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

MAP_FRAME_KEYS=set()
MAP_PALETTES={0x0F201510,0x0F201C1A,0x0F20161C,0x0F201A16}
PORTRAIT_PALETTES={0xFF263518,0xFF263506,0xFF263515}

def make_scenes(root,out):
    es=[l.split(',')for l in (root/'capture/01920.tiles').read_text().splitlines()]
    border=set();interior=set()
    for e in es:
        ly,x,y,k,p=int(e[0]),int(e[1]),int(e[2]),e[3],int(e[4])
        if ly:continue
        if (24<=x<232 and 24<=y<168)or(24<=x<152 and 184<=y<216):interior.add(k)
        if y in {16,168,176,216}or(x in {16,232}and 16<=y<176)or(x in {16,152}and 176<=y<224):border.add(k)
    MAP_FRAME_KEYS.update(border-interior)
    conditions=['<condition>worldmap,tileAtPosition,24,24,0000000000000000007F7F7F7F7F7F7F,0F20161C,N']
    backgrounds=['[worldmap]<background>worldmap.png,1,0,0,10']
    im=Image.new('RGBA',(1024,960),(8,14,18,255));d=ImageDraw.Draw(im)
    # Map board, with the terrain exactly inside the native route field.
    d.rounded_rectangle((64,64,960,704),radius=10,fill=(39,48,48),outline=(130,137,122),width=3)
    d.rectangle((80,80,944,688),fill=(12,23,26),outline=(12,15,16),width=6)
    terrain=Image.open(root/'art/map-terrain.png').convert('RGB').resize((832,576),Image.Resampling.LANCZOS)
    # Darken slightly so live paths and units read immediately.
    a=np.asarray(terrain,dtype=float)*.70;terrain=Image.fromarray(np.clip(a,0,255).astype('uint8'))
    im.paste(terrain,(96,96));d=ImageDraw.Draw(im)
    grid=Image.new('RGBA',im.size);g=ImageDraw.Draw(grid)
    for x in range(96,929,32):g.line((x,96,x,672),fill=(144,176,149,26),width=1)
    for y in range(96,673,32):g.line((96,y,928,y),fill=(144,176,149,26),width=1)
    im=Image.alpha_composite(im,grid);d=ImageDraw.Draw(im)
    d.rounded_rectangle((64,704,640,896),radius=8,fill=(24,34,35),outline=(130,137,122),width=3)
    d.rectangle((96,736,608,864),fill=(5,12,15))
    # Decorative scale ticks stay outside the clickable/live route region.
    for x in range(100,928,16):d.line((x,84,x,90),fill=(139,155,143),width=1)
    for y in range(100,672,16):d.line((84,y,90,y),fill=(139,155,143),width=1)
    im.save(out/'worldmap.png')

    states=json.loads((root/'capture/portraits.json').read_text())
    byid={s['id']:s for s in states};ids=list(range(10))
    art=Image.open(root/'art/portraits.png').convert('RGB').resize((1536,1024),Image.Resampling.LANCZOS)
    talking=Image.open(root/'art/enemy-talking.png').convert('RGB').resize((1024,512),Image.Resampling.LANCZOS)
    cells={0:0,1:3,2:1,3:4,4:2,6:5,8:5}
    mapping=[]
    for sid in ids:
        state=byid[sid];own={tuple(t[:4])for t in state['tiles']}
        others=set().union(*[{tuple(t[:4])for t in byid[j]['tiles']}for j in ids if j!=sid])
        unique=own-others
        x,y,key,p=min(unique,key=lambda t:(abs(t[1]-(96 if sid>=8 else 72)),abs(t[0]-200)))
        name=f'portrait{sid}'
        conditions.append(f'<condition>{name},spriteAtPosition,{x},{y},{key},{p:08X},N')
        guard=name if sid>=8 else f'radio&{name}'
        backgrounds.append(f'[{guard}]<background>{name}.png,1,0,0,20')
        if sid in cells:
            cell=cells[sid];col=cell%3;row=cell//3
            face=art.crop((col*512+112,row*512+40,col*512+456,row*512+474))
        else:
            col=0 if sid==5 else 1
            face=talking.crop((col*512+112,40,col*512+456,474));cell=f'talking{col}'
        face=face.resize((208,280),Image.Resampling.LANCZOS)
        overlay=Image.new('RGBA',(1024,960));overlay.paste(face,(728,216 if sid>=8 else 120))
        overlay.save(out/f'{name}.png')
        mapping.append({'state':sid,'cell':cell,'trigger':[x,y,key,f'{p:08X}'],'frames':state['frames']})
    (root/'validation/portrait_mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
    return conditions,backgrounds

def map_tile(key,p,indices,scale):
    if p not in MAP_PALETTES:return None
    ix=indices(key);a=np.zeros((8,8,4),np.uint8)
    if key in MAP_FRAME_KEYS:return scale(Image.fromarray(a))
    if p!=0x0F201510:
        # Leave coast/forest/desert to the painting; retain live white routes.
        a[ix==1]=[218,225,186,255]
    elif np.any(ix==2):
        # Native numbers are purple on white. New nodes invert that contrast
        # while preserving the exact tile text, flashing and selection state.
        a[ix==1]=[14,32,40,245];a[ix==2]=[239,220,157,255]
        a[ix==3]=[101,121,121,255]
    else:
        a[ix==1]=[176,187,173,255];a[ix==3]=[56,67,66,255]
    return scale(Image.fromarray(a))
