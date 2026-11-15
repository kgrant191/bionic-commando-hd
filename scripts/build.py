"""Build the Bionic Commando HD test pack from recorded CHR-RAM keys and art."""
from pathlib import Path
from collections import defaultdict, Counter
import os, re, json, math, ctypes, hashlib
import numpy as np
from scipy.ndimage import map_coordinates, binary_dilation
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from area13 import extend_area13
from area4 import extend_area4
from hud import health_tile
from water_edge import water_edge
from projectiles import make_projectile, extend_flares, GUARD as PROJECTILE_GUARD
from characters import CharacterMaterials
from poses import make_poses
from scenes import make_scenes, map_tile, MAP_PALETTES, PORTRAIT_PALETTES
from equipment import make_equipment
from closed_door import make_closed_door
from level_polish import environment as polish_environment, effects as polish_effects, area_clear, fade_aliases

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
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'feedback-v042/extra-keys.json').read_text()))
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'feedback-v050/extra-keys.json').read_text()))
for path in sorted((CAP/'ui').glob('*.tiles')):
    keys.extend((a[3],int(a[4]))for a in (l.split(',')for l in path.read_text().splitlines()))
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'area13/extra-keys.json').read_text()))
for l in (CAP/'area13/original-rules.txt').read_text().splitlines():
    if l.startswith('<tile>'):
        a=l[6:].split(',');keys.append((a[1],int(a[2],16)))
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'regression-extra-keys.json').read_text()))
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'area4/extra-keys.json').read_text()))
keys.extend((k,int(p,16))for k,p in json.loads((CAP/'water-extra-keys-v072.json').read_text()))
keys=list(dict.fromkeys(keys))
characters=CharacterMaterials(ROOT,indices,scale,tile)
scene_conditions,scene_backgrounds=make_scenes(ROOT,OUT)
equipment_conditions,equipment_backgrounds,equipment_hidden,equipment_tile=make_equipment(ROOT,OUT,indices,scale)
scene_conditions+=equipment_conditions;scene_backgrounds+=equipment_backgrounds
clear_conditions,clear_backgrounds,clear_guard,clear_tile=area_clear(ROOT,OUT,keys,indices,scale)
scene_conditions+=clear_conditions;scene_backgrounds+=clear_backgrounds
effect_tile,effect_pattern_count=polish_effects(ROOT)
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
machine_raw=np.asarray(Image.open(ROOT/'art/machinery-reference-v3.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS))
machine_x=np.interp(np.arange(1024),[0,32,160,544,608,800,928,1023],[0,36,170,556,616,809,941,1023])
machine_y=np.interp(np.arange(960),[0,64,128,320,384,448,512,640,768,928,959],[0,74,135,329,390,455,520,648,779,934,959])
my,mx=np.meshgrid(machine_y,machine_x,indexing='ij')
machine_aligned=Image.fromarray(np.stack([map_coordinates(machine_raw[:,:,c],[my,mx],order=1)for c in range(4)],2).astype('uint8'))

# Matching the original screenshot avoids a video-thread offset between the
# tile metadata and the screenshot. Crops come only from exact pixel matches.
painted={}; paint_sources={}
for n,name,palettes in [
    (3480,'level1-reference',{0x0f382818,0x0f271505,0x0f302118,0x0f211505}),
    (11640,'interior-reference',{0x0f21110b,0x0f261606,0x0f342303}),
    (7320,'control-reference',{0x0f301000,0x0f2b1b0b,0x0f2c1c0c,0x0f100005}),
    (38400,'reactor-reference',{0x0f221202,0x0f201000,0x0f372716,0x0f332313}),
    (21720,'tower-reference',{0x0f382818,0x0f271505,0x0f211505}),
    (25800,'machinery-reference-v3',{0x0f21110b,0x0f2a1908,0x0f342303}),
]:
    src=np.array(Image.open(CAP/f'{n:05d}.png').convert('RGB'))
    locations={}
    for yy in range(8,225):
        for xx in range(8,241):
            locations.setdefault(src[yy:yy+8,xx:xx+8].tobytes(),(xx,yy))
    art=Image.open(ROOT/f'art/{name}.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
    if name=='tower-reference':art=tower_aligned
    if name=='machinery-reference-v3':art=machine_aligned
    for key,p in sorted({(e[3],e[4])for e in entries(n)if e[0]==0 and e[4]in palettes}):
        if name in {'tower-reference','machinery-reference-v3'} and (key,p)in painted:continue
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

# The reactor's close view has a dedicated aligned painting. Match only the
# machinery rectangle so reused floor/platform patterns keep their prior art.
reactor_crop=Image.open(ROOT/'art/reactor-machine-v3.png').convert('RGBA').resize((320,704),Image.Resampling.LANCZOS)
reactor_original=np.array(Image.open(CAP/'38880.png').convert('RGB'))
reactor_locations={}
for y in range(24,193):
    for x in range(176,249):
        reactor_locations.setdefault(reactor_original[y:y+8,x:x+8].tobytes(),(x,y))
for key,p in sorted({(e[3],e[4])for e in entries(38880)if e[0]==0 and (e[4]&0xFFFFFF)in {0x332313,0x372716}}):
    if len(np.unique(indices(key)))==1:continue
    xy=reactor_locations.get(np.array(tile(key,p).convert('RGB')).tobytes())
    if xy is None:continue
    x,y=xy;normal=0x0F000000|(p&0xFFFFFF)
    painted[key,normal]=reactor_crop.crop(((x-176)*4,(y-24)*4,(x-168)*4,(y-16)*4))
    paint_sources[f'{key}:{normal:08X}']=[38880,x,y]

polished=polish_environment(ROOT,indices,tile)
painted.update(polished)
fades=fade_aliases(painted)

# Retain palette changes and damage effects. Detailed fallback colors are only
# applied to environment palettes, never to HUD, text, portraits or sprites.
env_palettes={0x0f382818,0x0f271505,0x0f302118,0x0f211505,
              0x0f21110b,0x0f261606,0x0f342303,0x0f301000,
              0x0f2b1b0b,0x0f2c1c0c,0x0f100005,
              0x0f221202,0x0f372716,0x0f332313,0x0f2a1908}
color_map={0x38:(207,203,142),0x28:(144,143,82),0x18:(74,76,42),
           0x27:(189,114,57),0x15:(124,52,43),0x05:(48,24,24),
           0x21:(86,150,202),0x11:(36,76,112),0x0b:(18,43,24),
           0x26:(206,117,77),0x16:(133,57,40),0x06:(61,28,24),
           0x34:(192,185,217),0x23:(117,111,152),0x03:(44,36,69),
           0x2a:(155,141,65),0x19:(81,78,30),0x08:(42,37,15)}
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
# Only the eight observed foam patterns are water. The same palette also
# belongs to lamps, windows, arches and pipes throughout the exterior.
water_keys={e[3]for e in entries(2640)if e[0]==0 and e[4]==0x0F302118 and e[2]>=208 and np.any(indices(e[3])==1)}
assert len(water_keys)==8,len(water_keys)
lamp_asset=Image.open(ROOT/'art/equipment-lamp-v4.png').convert('RGBA').crop((1024,0,1536,1024))
lamp_box=lamp_asset.getchannel('A').point(lambda a:255 if a>160 else 0).getbbox()
lamp_asset=lamp_asset.crop(lamp_box).resize((96,320),Image.Resampling.LANCZOS)
lamp_tiles={}
for ly,x,y,k,p,h,v in entries(7680):
    if ly==0 and 216<=x<240 and 162<=y<234 and len(np.unique(indices(k)))>1:
        lamp_tiles.setdefault((k,p),lamp_asset.crop(((x-216)*4,(y-162)*4,(x-208)*4,(y-154)*4)))
stone_material=water_source.crop((676,180,708,212))
steel_material=water_source.crop((412,110,444,142))
grass_keys={'000084484AEEF9D0FFFFFFFFFFFFF9D0','0000408892DFFD74FFFFFFFFFFFFFD74'}
# Repair only the contaminated pixels in affected structural crops; retain the
# accepted artwork and native transparency everywhere else. Water is separate.
seam_sheet=Image.open(ROOT/'art/exterior-seams-v4.1.png').convert('RGBA')
seam_cells=json.loads((CAP/'exterior-seams.json').read_text())
seam_patches={}
for i,cell in enumerate(seam_cells):
    cw,ch=seam_sheet.width//4,seam_sheet.height//3
    seam_patches[cell['key'],int(cell['palette'],16)]=seam_sheet.crop((i%4*cw,i//4*ch,(i%4+1)*cw,(i//4+1)*ch)).resize((32,32),Image.Resampling.LANCZOS)
seam_repairs=[]
# The source screenshot had Spencer in front of half the door. Map its full
# background pattern set from metadata instead of relying on visible matches.
door_source=Image.open(ROOT/'art/radio-door-v4.1.png').convert('RGBA').resize((128,128),Image.Resampling.LANCZOS)
door_tiles={}
for ly,x,y,k,p,h,v in entries(7320):
    if ly==0 and 32<=x<64 and 160<=y<192 and np.any(indices(k)):
        door_tiles.setdefault((k,p),door_source.crop(((x-32)*4,(y-160)*4,(x-24)*4,(y-152)*4)))
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

pose_conditions,pose_additions,virtual_keys=make_poses(ROOT,[(k,p)for k,p in keys if p!=0xFF36300F],rule,blank)
closed_conditions,closed_variants,closed_hidden=make_closed_door(ROOT)

a13_conditions,a13_backgrounds=extend_area13(ROOT,keys,indices,tile,scale,rule,blank)
scene_conditions+=a13_conditions;scene_backgrounds+=a13_backgrounds

a4_conditions,a4_backgrounds=extend_area4(ROOT,keys,indices,tile,scale,rule,blank)
scene_conditions+=a4_conditions;scene_backgrounds+=a4_backgrounds

scene_conditions+=water_edge(ROOT,rule)
scene_conditions+=extend_flares(ROOT,keys,rule)
projectile_tile=make_projectile(ROOT)

for key,p in keys:
    projectile_im=projectile_tile(key,p)
    if projectile_im is not None:rule(key,p,projectile_im,PROJECTILE_GUARD)
    hud_im=health_tile(key,p,tile)
    if hud_im is not None:rule(key,p,hud_im,'!title&!worldmap&!equipment&!radio&!areaClear')
    if p==0x0F200F0F:rule(key,p,blank,'areaClear&clearHeaderY0&clearHeaderY1&clearHeaderX0&clearHeaderX1')
    clear_im=clear_tile(key,p)
    if clear_im is not None:rule(key,p,clear_im,clear_guard)
    if (key,p)in equipment_hidden:rule(key,p,blank,equipment_hidden[key,p])
    equip_im=equipment_tile(key,p)
    if equip_im is not None:
        rule(key,p,equip_im,'equipment');rule(key,p,equip_im,'worldmap')
    if (key,p)in title_keys or p>>24==255:rule(key,p,blank,'title')
    if (key,p)in radio_keys:rule(key,p,transparent_ink(key,p)if(key,p)in radio_text else blank,'radio')
    if (key,p)in portrait_extra:rule(key,p,blank,'radio')
    if p in PORTRAIT_PALETTES:
        rule(key,p,blank,'radio')
        rule(key,p,blank,'portrait8')
        rule(key,p,blank,'portrait9')
    map_im=map_tile(key,p,indices,scale)
    if map_im is not None:rule(key,p,map_im,'worldmap')
    # Background color cycles change the first palette byte. Reuse the
    # painted material and apply the original color flash to index-zero pixels.
    actual_p=p
    fade_factor=1
    if (key,p)in fades:p,fade_factor=fades[key,p]
    canonical=0x0F000000|(p&0xFFFFFF)
    flashing=p>>24 not in {0x0F,0xFF} and (canonical in env_palettes or (key,canonical)in painted)
    if flashing:p=canonical
    ix=indices(key)
    im=painted.get((key,p))
    # A palette boundary can turn the same beam/wall pattern into a sky-edge
    # tile. Share its painting, then apply that tile's own transparent aperture.
    if im is None and p in {0x0f211505,0x0f271505}:
        im=painted.get((key,0x0f271505))or painted.get((key,0x0f211505))
    if im is None and p in {0x0f302118,0x0f382818}:
        im=painted.get((key,0x0f382818))or painted.get((key,0x0f302118))
    if im is None and p==0x0f302118 and key not in grass_keys|water_keys:
        im=stone_material.copy();a=np.array(im)
        a[np.repeat(np.repeat(ix==0,4,0),4,1)]=[0,0,0,255]
        im=Image.fromarray(a)
    if im is None and p in {0x0f211505,0x0f271505}:
        # Use the swatch only for subtle material grain. Copying an arbitrary
        # beam crop would put disconnected braces/rivets into these edge cells.
        colors=np.array([[0,0,0,255],[197,105,55,255],[139,49,28,255],[48,22,18,255]],dtype=np.uint8)
        a=np.array(scale(Image.fromarray(colors[ix])))
        grain=np.array(steel_material.filter(ImageFilter.GaussianBlur(.7)),float)[:,:,:3].mean(2)
        grain=np.clip((grain-grain.mean())*.12,-6,6)
        solid=np.repeat(np.repeat(ix>0,4,0),4,1)
        a[:,:,:3]=np.clip(a[:,:,:3].astype(float)+grain[:,:,None]*solid[:,:,None],0,255)
        im=Image.fromarray(a)
    if im is None:im=fallback(key,p)
    sprite_im=characters.render(key,p)
    if sprite_im is not None:im=sprite_im;sprite_count+=1
    ix=indices(key)
    if (key,p)in lamp_tiles:
        im=lamp_tiles[key,p]
    elif p==0x0f302118 and key in water_keys:
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
    if p==0x0f382818 and (key,p)not in painted and len(np.unique(ix))>1:
        # Remaining wall/arch edge variants used to retain the coarse NES
        # decoration. Keep their exact void boundaries but use painted stone.
        im=(stone_material if np.any(ix==0)else flat_stucco).copy()
        a=np.array(im);void=np.repeat(np.repeat(ix==0,4,0),4,1)
        a[void]=[0,0,0,255];im=Image.fromarray(a)
    if p==0x0f2b1b0b and np.all(ix==2):im=control_source.crop((280,220,312,252))
    if p==0x0f221202 and np.all(ix==3):im=reactor_source.crop((400,216,432,248))
    if (key,p)in seam_patches:
        a=np.array(im);rgb=a[:,:,:3].astype(float)
        blue=(rgb[:,:,2]>rgb[:,:,0]*1.15)&(rgb[:,:,2]>rgb[:,:,1]*.88)&(rgb[:,:,2]-rgb[:,:,0]>22)&(rgb[:,:,2]>80)&(a[:,:,3]>0)
        repair=binary_dilation(blue,iterations=1)&(a[:,:,3]>0)
        patch=np.array(seam_patches[key,p]);a[repair,:3]=patch[repair,:3]
        im=Image.fromarray(a)
        if blue.any():seam_repairs.append({'key':key,'palette':f'{actual_p:08X}','blue_pixels':int(blue.sum()),'patched_pixels':int(repair.sum())})
    if (key,p)in door_tiles:im=door_tiles[key,p]
    effect_im=effect_tile(key,p)
    if effect_im is not None:im=effect_im
    if (key,p)in closed_hidden:im=blank
    for guard,overlay in closed_variants.get((key,p),[]):
        rule(key,actual_p,Image.alpha_composite(im.convert('RGBA'),overlay),guard)
    if flashing:
        a=np.array(im);mask=np.repeat(np.repeat(ix==0,4,0),4,1)
        a[mask,:3]=PAL[(actual_p>>24)&63,:3];a[mask,3]=255
        im=Image.fromarray(a)
    if fade_factor!=1:
        a=np.array(im);a[:,:,:3]=(a[:,:,:3].astype(float)*fade_factor).astype('uint8');im=Image.fromarray(a)
    rule(key,actual_p,im)

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
header=['# Bionic Commando HD v0.7.5 - Knife guard and active flare corrections','<ver>109','<scale>4',
        '<supportedRom>D3A4BFD995D18C4A386971631759AECA3A7CFF8D',
        '<overscan>8,0,8,0','<img>tiles.png',
        '<condition>title,tileAtPosition,128,64,3D3D3E3E3F3F3F3FDADADDDDDEDEDFDF,0F20152B,N',
        '<condition>radio,tileAtPosition,0,0,0000000000000000FFFFFFFFFFFFFFFF,0F090909,N',
        '<condition>screenEnabled,memoryCheckConstant,00FF,==,1A',
        '[screenEnabled]<background>sky.png,1,0,0,0',
        '[title]<background>title.png,1,0,0,10',
        '[radio]<background>radio.png,1,0,0,10']
header=header[:8]+['<options>disableSpriteLimit']+scene_conditions+pose_conditions+closed_conditions+header[8:]+pose_additions+scene_backgrounds
from additions import coalesce_additions
header,rules,merged_additions=coalesce_additions(header,rules)
(OUT/'hires.txt').write_text('\n'.join(header+rules)+'\n')
stats={'version':'0.7.5','projectile_palette_variants':sum(projectile_tile(k,p) is not None for k,p in keys),'merged_duplicate_sprite_additions':merged_additions,'area4_guard_pose_records':6,'area4_guard_paintings':6,'area4_inventory_icons':2,'area4_boss_portrait_expressions':2,'area13_red_rifle_guard_poses':3,'area13_white_guard_poses':8,'area13_contact_poses':4,'area13_neutral_guard_poses':3,'area13_portrait_characters':4,'area13_portrait_expressions':8,'builder_tile_palette_keys':raw_key_count,'captured_tile_palette_keys':len(keys),'painted_environment_keys':len(painted),
       'painted_spencer_pose_records':22,'spencer_paintings':19,'painted_enemy_poses':12,'virtual_sprite_keys':len({tuple(l[10:].split(',')[4:6])for l in header if l.startswith('<addition>')}),'sprite_material_keys':sprite_count,'portrait_expressions':8,'portrait_screen_states':10,'dense_sprite_capture_interval':15,
       'water_patterns':len(water_keys),'lamp_patterns':len(lamp_tiles),
       'door_patterns':len(door_tiles),'exterior_seam_patterns':len(seam_patches),
       'polished_fixture_patterns':len(polished),'painted_effect_patterns':effect_pattern_count,
       'environment_fade_aliases':len(fades),'feedback_v050_new_keys':86,
       'closed_door_sprite_patterns':len(closed_hidden),'closed_door_background_cells':sum(map(len,closed_variants.values())),
       'tile_rules':len(rules),'unique_atlas_tiles':len(atlas),'scale':4,
       'output_size':[1024,896],'overscan_top_bottom':8}
(ROOT/'build_stats.json').write_text(json.dumps(stats,indent=2)+'\n')
(ROOT/'validation/art_mapping.json').write_text(json.dumps(paint_sources,indent=2)+'\n')
(ROOT/'validation/seam_mapping.json').write_text(json.dumps({'repairs':seam_repairs,'door_patterns':[[k,f'{p:08X}']for k,p in door_tiles]},indent=2)+'\n')
print(json.dumps(stats,indent=2))
