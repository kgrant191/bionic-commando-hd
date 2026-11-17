"""Apply the reviewed Area 5 fixes to the exact v0.9.6 runtime baseline.

Usage: python scripts/apply_v097.py BASELINE_ZIP CAPTURE_TILES OUTPUT_PACK
This preserves all earlier runtime rules and assets byte-for-byte except the
version notes and explicitly selected generator flash rules.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys,zipfile
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
baseline, captures, dest=map(Path,sys.argv[1:4])
from runtime_baseline import copy_baseline
baseline_sha256=copy_baseline(baseline,dest,'096')
lines=(dest/'hires.txt').read_text().splitlines()
images=[Image.open(dest/l[5:]).convert('RGBA') for l in lines if l.startswith('<img>')]
new_id=len(images);atlas=Image.new('RGBA',(2048,2048));cache={};pieces=[]
def place(im):
    assert im.size==(32,32)
    key=im.tobytes()
    if key not in cache:
        i=len(cache);x=i%64*32;y=i//64*32
        assert y<atlas.height
        atlas.paste(im,(x,y));cache[key]=(x,y)
    return cache[key]
def parse(line):
    prefix,data=line.split('<tile>',1)
    return prefix,data.split(',')
def rule(k,p,im,guard):
    x,y=place(im)
    return f'[{guard}]<tile>{new_id},{k},{p:08X},{x},{y},1,N'
def crop(a):
    x,y=map(int,a[3:5]);return images[int(a[0])].crop((x,y,x+32,y+32))
def entries(f):
    return [(int(l),int(x),int(y),k,int(p),int(h),int(v)) for l,x,y,k,p,h,v in (l.split(',') for l in (captures/f'{f:05d}.tiles').read_text().splitlines())]

# Missing damage colors must receive BOTH native suppression rules and the
# matching additional HD sprites; adding only one leaves double figures.
known=defaultdict(set);bykey=defaultdict(list);additions=defaultdict(list)
for line in lines:
    if '<tile>' in line:
        g,a=parse(line);known[a[1]].add(int(a[2],16));bykey[a[1],int(a[2],16)].append(line)
    elif line.startswith('<addition>'):
        a=line[10:].split(',');additions[a[0],int(a[1],16)].append(a)
missing=set();observed_damage=set()
for f in sorted(captures.glob('*.tiles')):
    for row in f.read_text().splitlines():
        ly,x,y,k,p,h,v=row.split(',');p=int(p)
        if ly=='1' and p in {0xFF201515,0xFF202015}:
            observed_damage.add((k,p))
            if p not in known[k]:missing.add((k,p))
aliases={}
for k,p in observed_damage:
    source=0xFF36060F if p==0xFF201515 else 0xFF202A0F
    assert source in known[k],(k,hex(p))
    aliases[k,p]=source
extra_add=[]
for (k,p),source in list(aliases.items()):
    if p in known[k]:continue
    for a in additions[k,source]:
        a=a.copy();a[1]=f'{p:08X}';a[5]=f'{p:08X}';extra_add.append('<addition>'+','.join(a))
        virtual=a[4]
        if p not in known[virtual]:aliases[virtual,p]=source
sprite_rules=[]
for (k,p),source in sorted(aliases.items()):
    for line in bykey[k,source]:
        g,a=parse(line);a=a.copy();a[2]=f'{p:08X}'
        # Preserve native hit feedback using the same red tint as the other
        # existing HD damage poses, including their transparent pixels.
        im=crop(a);ar=np.array(im);ar[:,:,:3]=np.clip(ar[:,:,:3].astype(float)*[1.15,.72,.65],0,255).astype('uint8')
        x,y=place(Image.fromarray(ar));a[0]=str(new_id);a[3:5]=[str(x),str(y)]
        sprite_rules.append(g+'<tile>'+','.join(a))

# The complete roof is selected by native roof landmarks, so repeating CHR
# patterns do not force identical cracks or cut through individual posts.
roof=Image.open(ROOT/'art/area5-rooftop-v097.png').convert('RGBA').resize((384,192),Image.Resampling.LANCZOS)
cells={(x,y):(k,p)for ly,x,y,k,p,h,v in entries(3) if ly==0 and 65<=x<161 and 30<=y<78 and p==0x0F261606 and k!='0000000000000000FFFFFFFFFFFFFFFF'}
anchors=[(65,62),(153,62),(145,30)];conditions=[];roof_rules=[];cond_cache={}
guard='area5&!title&!worldmap&!equipment&!radio&!areaClear'
for (x,y),(k,p) in sorted(cells.items()):
    im=roof.crop(((x-65)*4,(y-30)*4,(x-57)*4,(y-22)*4))
    for ax,ay in anchors:
        ak,ap=cells[ax,ay];token=ax-x,ay-y,ak,ap
        if token not in cond_cache:
            name=f'area5Roof097_{len(cond_cache)}';cond_cache[token]=name
            conditions.append(f'<condition>{name},tileNearby,{ax-x},{ay-y},{ak},{ap:08X},N')
        roof_rules.append(rule(k,p,im,guard+'&'+cond_cache[token]))

# Flash only illuminated material. Opaque black padding in the existing
# generator atlas must remain black instead of turning into red rectangles.
flash_count=0;flash_pixels=0
for i,line in enumerate(lines):
    if '<tile>' not in line or not line.startswith('[area5&'):continue
    g,a=parse(line);p=int(a[2],16)
    if p>>24!=0x16:continue
    normal=[l for l in bykey[a[1],(p&0xFFFFFF)|0x0F000000] if parse(l)[0]==g]
    if not normal:continue
    base=crop(parse(normal[0])[1]);original=crop(a)
    if base.tobytes()==original.tobytes():continue
    ar=np.array(base);rgb=ar[:,:,:3].astype(float)
    weight=np.clip((rgb.max(axis=2)-12)/64,0,1)[:,:,None]
    tinted=np.clip(rgb*.65+[135,40,28],0,255)
    ar[:,:,:3]=np.rint(rgb*(1-weight)+tinted*weight).astype('uint8')
    x,y=place(Image.fromarray(ar));a[0]=str(new_id);a[3:5]=[str(x),str(y)];lines[i]=g+'<tile>'+','.join(a)
    flash_count+=1;flash_pixels+=int((weight[:,:,0]==0).sum())

lines[0]='# Bionic Commando HD v0.9.7 - Area 5 roof, damage palettes and generator flash seams'
insert=next(i for i,l in enumerate(lines)if '<tile>'in l)
lines[insert:insert]=['<img>area5-v097.png']+conditions+extra_add+roof_rules+sprite_rules
(dest/'hires.txt').write_text('\n'.join(lines)+'\n')
atlas.crop((0,0,2048,((len(cache)+63)//64)*32)).save(dest/'area5-v097.png')
readme=(dest/'README.txt').read_text().replace('v0.9.6','v0.9.7')
readme+='\nV0.9.7: Painted rooftop railing and emblem. Complete Spencer/enemy damage-palette mappings. Generator glow preserves black recesses; original hit timing retained.\n'
(dest/'README.txt').write_text(readme)
report={'version':'0.9.7','baseline_sha256':baseline_sha256,'missing_native_key_palette_pairs':len(missing),'observed_damage_pairs_repaired':len(observed_damage),'aliases_including_virtual':len(aliases),'new_additions':len(extra_add),'new_sprite_rules':len(sprite_rules),'roof_cells':len(cells),'roof_conditions':len(conditions),'flash_rules_updated':flash_count,'unlit_pixels_preserved':flash_pixels,'new_atlas_cells':len(cache),'boss_rules_changed':0}
(ROOT/'validation').mkdir(exist_ok=True)
(ROOT/'validation/v097-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
