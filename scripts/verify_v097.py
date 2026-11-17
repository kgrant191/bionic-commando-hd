"""Verify complete movie parity, rule preservation and image-change scope."""
from pathlib import Path
from collections import Counter
import json,re,sys,hashlib
import numpy as np
from PIL import Image
base,pack,replay=map(Path,sys.argv[1:4]);root=Path(__file__).resolve().parents[1]
before=(base/'hires.txt').read_text().splitlines();after=(pack/'hires.txt').read_text().splitlines()
def tile(l):return l.split('<tile>',1)[1].split(',')
removed=list((Counter(before)-Counter(after)).elements())
assert all(l.startswith('# Bionic')or('<tile>'in l and l.startswith('[area5&')and int(tile(l)[2],16)>>24==0x16)for l in removed)
changed_flash={(tile(l)[1],int(tile(l)[2],16))for l in removed if '<tile>'in l}
new_roof={(tile(l)[1],int(tile(l)[2],16))for l in after if 'area5Roof097_'in l and '<tile>'in l}
images=[];known=set();adds=[];conditions=set()
for l in after:
 if l.startswith('<img>'):images.append(Image.open(pack/l[5:]))
 if l.startswith('<condition>'):
  name=l[11:].split(',')[0];assert name not in conditions;conditions.add(name)
 if '<tile>'in l:
  a=tile(l);i,x,y=int(a[0]),int(a[3]),int(a[4]);assert 0<=i<len(images)and x>=0 and y>=0 and x+32<=images[i].width and y+32<=images[i].height
  known.add((a[1],int(a[2],16)))
 if l.startswith('<addition>'):adds.append(tuple(l[10:].split(',')))
assert len({a[:4]+a[6:] for a in adds})==len(adds)
assert all((a[0],int(a[1],16))in known and(a[4],int(a[5],16))in known for a in adds)
for p in base.iterdir():
 if p.name not in {'hires.txt','README.txt'}:assert p.read_bytes()==(pack/p.name).read_bytes(),p.name
frames=1940; mismatches=[]
for n in range(1,frames+1):
 for ext in ['ram','ppu']:
  f=f'{n:05d}.{ext}'
  if (replay/'original/frames'/f).read_bytes()!=(replay/'final/frames'/f).read_bytes():mismatches.append(f)
assert not mismatches,mismatches
log=(replay/'final/log.txt').read_text();assert not re.search(r'\[HDPack\].*(error|Error)|[Ss]cript error|Exception',log)
assert int((replay/'final/home/done').read_text())==frames
def entries(n):
 return [(int(l),int(x),int(y),k,int(p))for l,x,y,k,p,h,v in (s.split(',') for s in (replay/f'before/tiles/{n:05d}.tiles').read_text().splitlines())]
count=0;outside=0;changed=[];boss_unchanged=0;damage_coverage=set();target_frames=[]
for f in sorted((replay/'final/frames').glob('*.png')):
 n=int(f.stem);a=np.array(Image.open(replay/'before/frames'/f.name).convert('RGBA'));b=np.array(Image.open(f).convert('RGBA'));assert a.shape==b.shape==(896,1024,4)
 diff=np.any(a!=b,axis=2);allowed=np.zeros((896,1024),bool)
 def allow(x,y,w,h):
  x0=max(x*4,0);x1=min((x+w)*4,1024);y0=max((y-8)*4,0);y1=min((y+h-8)*4,896)
  if x0<x1 and y0<y1:allowed[y0:y1,x0:x1]=True
 for frame in [n,max(1,n-1)]:
  for ly,x,y,k,p in entries(frame):
   if ly==0 and((k,p)in new_roof or(k,p)in changed_flash):allow(x,y,8,8)
   if ly==1 and p in {0xFF201515,0xFF202015}:
    assert (k,p)in known,(n,k,hex(p));damage_coverage.add((k,p));allow(x-48,y-32,112,96)
 outside+=int((diff&~allowed).sum());count+=1
 if diff.any():changed.append(n)
 if 400<=n<=1116 and not diff.any():boss_unchanged+=1
assert outside==0,outside
report={'version':'0.9.7','recording':'Bionic Commando (USA)(8).mmo','native_frames_checked':frames,'RAM_mismatches':[],'PPU_mismatches':[],'screenshots_compared':count,'changed_pixels_outside_targets':outside,'boss_room_screenshots_identical':boss_unchanged,'observed_damage_pairs_with_rules':len(damage_coverage),'original_nonflash_rules_preserved':True,'prior_image_assets_unchanged':True,'duplicate_sprite_additions':0,'changed_screenshot_frames':changed,'limits':'Full recording replayed; screenshots captured every three frames. Unrecorded states remain untested. Boss design and animation rules unchanged.'}
(root/'validation/v097-regression.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='changed_screenshot_frames'},indent=2))
