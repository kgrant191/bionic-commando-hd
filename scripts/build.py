"""Build the Bionic Commando HD test pack from recorded CHR-RAM keys and art."""
from pathlib import Path
from collections import defaultdict, Counter
import os, re, json, math, ctypes, hashlib
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from characters import CharacterMaterials
from scenes import make_scenes, map_tile, MAP_PALETTES, PORTRAIT_PALETTES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'pack'; OUT.mkdir(exist_ok=True)
CAP=ROOT/'capture'
PAL=np.array([[int(h,16)>>16&255,int(h,16)>>8&255,int(h,16)&255,255]
              for h in re.findall('0x([A-Fa-f0-9]+)',(ROOT/'tools/palette.inc').read_text())],dtype=np.uint8)
lib=ctypes.CDLL(os.environ['BIONIC_XBRZ_LIBRARY'])
lib.scale4.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
def indices(key):
    a=np.unpackbits(np.frombuffer(bytes.fromhex(key),dtype=np.uint8)).reshape(16,8)
    return a[:8]+2*a[8:]
def tile(key,p):
    colors=np.array([(p>>s)&63 for s in (24,16,8,0)])
    ix=indices(key); a=PAL[colors][ix].copy()
    if p>>24==255:a[ix==0]=0
    return Image.fromarray(a)
def scale(im):
    a=np.array(im.convert('RGBA'))[:,:,[2,1,0,3]].copy();h,w=a.shape[:2]
    b=np.zeros((h*4,w*4,4),np.uint8)
    lib.scale4(a.ctypes.data,b.ctypes.data,w,h)
    return Image.fromarray(b[:,:,[2,1,0,3]])
def entries(n):
    return [(int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6]))
            for a in (l.split(',') for l in (CAP/f'{n:05d}.tiles').read_text().splitlines())]
keys=[]
for l in (CAP/'original-rules.txt').read_text().splitlines():
    if l.startswith('<tile>'):
        a=l[6:].split(',');keys.append((a[1],int(a[2],16)))
keys=list(dict.fromkeys(keys))
raw_key_count=len(keys)
for path in sorted(CAP.glob('*.tiles')):
    keys.extend((e[3],e[4])for e in entries(int(path.stem)))
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'sprite-keys.json').read_text()))
keys=list(dict.fromkeys(keys))
characters=CharacterMaterials(ROOT,indices,scale,tile)
scene_conditions,scene_backgrounds=make_scenes(ROOT,OUT)
sprite_count=0
portrait_extra={(k,int(p,16))for k,p in json.loads((CAP/'portrait-extra-keys.json').read_text())}

# Align generated tower geometry to the source level before extracting tiles.
# Piecewise landmarks preserve the source platform/door boundaries precisely.
tower_raw=Image.open(ROOT/'art/tower-reference.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
tower_x=np.interp(np.arange(1024),[0,376,504,632,760,1023],[0,355,473,601,720,1023])
tower_y=np.interp(np.arange(960),[0,376,408,504,536,632,664,824,896,952,959],[0,305,333,416,447,548,572,735,804,876,959])
ty,tx=np.meshgrid(tower_y,tower_x,indexing='ij');ta=np.asarray(tower_raw)
tower_aligned=Image.fromarray(np.stack([map_coordinates(ta[:,:,c],[ty,tx],order=1)for c in range(4)],2).astype('uint8'))
flat_stucco=np.asarray(tower_aligned.crop((448,432,480,464)).filter(ImageFilter.GaussianBlur(.6)),dtype=float).copy()
center=flat_stucco[:,:,:3].mean((0,1));fy,fx=np.mgrid[:32,:32]
edge=np.minimum.reduce([fx,fy,31-fx,31-fy]);blend=np.clip(edge/4,0,1)[:,:,None]
flat_stucco[:,:,:3]=center+(flat_stucco[:,:,:3]-center)*.42*blend
flat_stucco=Image.fromarray(np.clip(flat_stucco,0,255).astype('uint8'))

# Matching the original screenshot avoids a video-thread offset between the
# tile metadata and the screenshot. Crops come only from exact pixel matches.
painted={}; paint_sources={}
for n,name,palettes in [
    (3480,'level1-reference',{0x0f382818,0x0f271505,0x0f302118,0x0f211505}),
    (11640,'interior-reference',{0x0f21110b,0x0f261606,0x0f342303}),
    (7320,'control-reference',{0x0f301000,0x0f2b1b0b,0x0f2c1c0c,0x0f100005}),
    (38400,'reactor-reference',{0x0f221202,0x0f201000,0x0f372716,0x0f332313}),
    (21720,'tower-reference',{0x0f382818,0x0f271505,0x0f211505}),
]:
    src=np.array(Image.open(CAP/f'{n:05d}.png').convert('RGB'))
    locations={}
    for yy in range(8,225):
        for xx in range(8,241):
            locations.setdefault(src[yy:yy+8,xx:xx+8].tobytes(),(xx,yy))
    art=Image.open(ROOT/f'art/{name}.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
    if name=='tower-reference':art=tower_aligned
    for key,p in sorted({(e[3],e[4])for e in entries(n)if e[0]==0 and e[4]in palettes}):
        if name=='tower-reference' and (key,p)in painted:continue
        ix=indices(key)
        if len(np.unique(ix))==1:continue
        template=np.array(tile(key,p).convert('RGB'))
        match=locations.get(template.tobytes())
        if match is None:continue
        x,y=match
        im=art.crop((x*4,y*4,(x+8)*4,(y+8)*4))
        # Preserve sky openings exactly; generated painted motifs must never
        # obscure collision silhouettes or the bionic arm's anchor points.
        if p in {0x0f302118,0x0f211505}:
            sky=ix==(2 if p==0x0f302118 else 1)
            # Water tiles contain substantial white foam and stay opaque.
            if not(p==0x0f302118 and (ix==1).sum()>3):
                a=np.array(im);a[np.repeat(np.repeat(sky,4,0),4,1),3]=0;im=Image.fromarray(a)
        painted[(key,p)]=im;paint_sources[f'{key}:{p:08X}']=[n,x,y]

# Retain palette changes and damage effects. Detailed fallback colors are only
# applied to environment palettes, never to HUD, text, portraits or sprites.
env_palettes={0x0f382818,0x0f271505,0x0f302118,0x0f211505,
              0x0f21110b,0x0f261606,0x0f342303,0x0f301000,
              0x0f2b1b0b,0x0f2c1c0c,0x0f100005,
              0x0f221202,0x0f372716,0x0f332313}
color_map={0x38:(207,203,142),0x28:(144,143,82),0x18:(74,76,42),
           0x27:(189,114,57),0x15:(124,52,43),0x05:(48,24,24),
           0x21:(86,150,202),0x11:(36,76,112),0x0b:(18,43,24),
           0x26:(206,117,77),0x16:(133,57,40),0x06:(61,28,24),
           0x34:(192,185,217),0x23:(117,111,152),0x03:(44,36,69)}
def fallback(key,p):
    im=tile(key,p)
    if p in env_palettes:
        ix=indices(key);a=np.array(im)
        for i,s in enumerate((24,16,8,0)):
            c=(p>>s)&63
            if c in color_map:a[ix==i,:3]=color_map[c]
        im=Image.fromarray(a)
    return scale(im)

title_keys=set();title_text=set();title_sprites=set();radio_keys=set();radio_text=set()
for path in sorted(CAP.glob('*.tiles')):
    n=int(path.stem); es=entries(n)
    # Radio's forest-green surround is unique in this recording.
    is_radio=any(e[0]==0 and e[1]==0 and e[2]==0 and e[3]=='0000000000000000FFFFFFFFFFFFFFFF' and e[4]==0x0f090909 for e in es)
    if is_radio:
        for ly,x,y,k,p,h,v in es:
            if ly==0:
                radio_keys.add((k,p))
                if 24<=x<168 and 24<=y<104 and np.any(indices(k)):
                    radio_text.add((k,p))
    if n<=600:
        for ly,x,y,k,p,h,v in es:
            if ly==0:
                title_keys.add((k,p))
                if y>=160 and np.any(indices(k)):title_text.add((k,p))
            else:title_sprites.add((k,p))

blank=Image.new('RGBA',(32,32));atlas=[];cache={};rules=[]
water_source=Image.open(ROOT/'art/level1-reference.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
control_source=Image.open(ROOT/'art/control-reference.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
reactor_source=Image.open(ROOT/'art/reactor-reference.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
def add(im):
    im=im.convert('RGBA');h=hashlib.sha256(im.tobytes()).digest()
    if h not in cache:cache[h]=len(atlas);atlas.append(im)
    i=cache[h];return i%64*32,i//64*32
def rule(k,p,im,cond=None):
    x,y=add(im)
    rules.append((f'[{cond}]'if cond else '')+f'<tile>0,{k},{p:08X},{x},{y},1,N')
def transparent_ink(key,p):
    a=np.array(tile(key,p));a[indices(key)==0]=0
    return scale(Image.fromarray(a))

for key,p in keys:
    if (key,p)in title_keys or p>>24==255:rule(key,p,blank,'title')
    if (key,p)in radio_keys:rule(key,p,transparent_ink(key,p)if(key,p)in radio_text else blank,'radio')
    if (key,p)in portrait_extra:rule(key,p,blank,'radio')
    if p in PORTRAIT_PALETTES:
        rule(key,p,blank,'radio')
        rule(key,p,blank,'portrait8')
        rule(key,p,blank,'portrait9')
    map_im=map_tile(key,p,indices,scale)
    if map_im is not None:rule(key,p,map_im,'worldmap')
    im=painted.get((key,p))
    if im is None:im=fallback(key,p)
    sprite_im=characters.render(key,p)
    if sprite_im is not None:im=sprite_im;sprite_count+=1
    ix=indices(key)
    if p==0x0f302118 and np.any(ix==1):
        # All phases of the water use the same painted material family.
        sx=(int(key[:8],16)%16)*32
        im=water_source.crop((sx,872,sx+32,904))
    elif p in {0x0f302118,0x0f211505}:
        sky=ix==(2 if p==0x0f302118 else 1)
        a=np.array(im); mask=np.repeat(np.repeat(sky,4,0),4,1)
        a[mask,3]=0
        # Remove residual sky color in painted beam edges after enforcing
        # the original sky aperture, without altering game geometry.
        blue=(a[:,:,2]>a[:,:,0]*1.18)&(a[:,:,2]>140)&(a[:,:,1]>100)&~mask
        a[blue,:3]=[40,29,24]
        im=Image.fromarray(a)
    if p==0x0f382818:
        a=np.array(im);blue=(a[:,:,2]>a[:,:,0]*1.35)&(a[:,:,2]>a[:,:,1]*1.10)
        a[blue,:3]=[112,119,65];im=Image.fromarray(a)
    if p==0x0f382818 and np.all(ix==2):im=flat_stucco
    if p==0x0f2b1b0b and np.all(ix==2):im=control_source.crop((280,220,312,252))
    if p==0x0f221202 and np.all(ix==3):im=reactor_source.crop((400,216,432,248))
    rule(key,p,im)

for name in ['title','radio']:
    asset=Image.open(ROOT/f'art/{name}.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
    if name=='title':
        font_path=os.environ.get('BIONIC_UI_FONT','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
        d=ImageDraw.Draw(asset)
        d.text((512,664),'PRESS START',anchor='mm',font=ImageFont.truetype(font_path,34),fill=(240,239,219),stroke_width=2,stroke_fill=(7,13,20))
        copyright_lines=['TM AND ©1988 CAPCOM CO.,LTD.','©1988 CAPCOM U.S.A.,INC.','LICENSED BY NINTENDO OF AMERICA INC.']
        font=ImageFont.truetype(font_path,18)
        for i,line in enumerate(copyright_lines):d.text((512,840+i*24),line,anchor='mm',font=font,fill=(215,220,225),stroke_width=1,stroke_fill=(6,10,16))
    asset.save(OUT/f'{name}.png')
scene=Image.open(ROOT/'art/level1-reference.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
tower_raw.crop((0,0,350,328)).resize((1024,960),Image.Resampling.BICUBIC).save(OUT/'sky.png')
im=Image.new('RGBA',(2048,math.ceil(len(atlas)/64)*32))
for i,t in enumerate(atlas):im.paste(t,(i%64*32,i//64*32))
im.save(OUT/'tiles.png',optimize=True)
header=['# Bionic Commando HD v0.2.0 - map, radio and sprite detail pass','<ver>109','<scale>4',
        '<supportedRom>D3A4BFD995D18C4A386971631759AECA3A7CFF8D',
        '<overscan>8,0,8,0','<img>tiles.png',
        '<condition>title,tileAtPosition,0,0,00000000000000000000000000000000,0F20152B,N',
        '<condition>radio,tileAtPosition,0,0,0000000000000000FFFFFFFFFFFFFFFF,0F090909,N',
        '<background>sky.png,1,0,0,0',
        '[title]<background>title.png,1,0,0,10',
        '[radio]<background>radio.png,1,0,0,10']
header=header[:8]+scene_conditions+header[8:]+scene_backgrounds
(OUT/'hires.txt').write_text('\n'.join(header+rules)+'\n')
stats={'builder_tile_palette_keys':raw_key_count,'captured_tile_palette_keys':len(keys),'painted_environment_keys':len(painted),
       'sprite_material_keys':sprite_count,'portrait_expressions':8,'portrait_screen_states':10,'dense_sprite_capture_interval':15,
       'tile_rules':len(rules),'unique_atlas_tiles':len(atlas),'scale':4,
       'output_size':[1024,896],'overscan_top_bottom':8}
(ROOT/'build_stats.json').write_text(json.dumps(stats,indent=2)+'\n')
(ROOT/'validation/art_mapping.json').write_text(json.dumps(paint_sources,indent=2)+'\n')
print(json.dumps(stats,indent=2))
