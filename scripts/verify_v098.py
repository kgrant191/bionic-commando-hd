"""Verify the exhaust patch and recorded gameplay without changing game state."""
from pathlib import Path
from collections import Counter
import json,re
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent
base=R/'baseline-v097';pack=ROOT/'pack';replay=R/'replay/8'
HEAD='C7C7C7D7C7C7C7FF4141796979797979'
before=(base/'hires.txt').read_text().splitlines();after=(pack/'hires.txt').read_text().splitlines()
removed=list((Counter(before)-Counter(after)).elements())
assert len(removed)==1 and removed[0].startswith('# Bionic')
images=[];known=set();adds=[];conditions=set()
for l in after:
 if l.startswith('<img>'):images.append(Image.open(pack/l[5:]))
 if l.startswith('<condition>'):
  name=l[11:].split(',')[0];assert name not in conditions;conditions.add(name)
 if '<tile>'in l:
  a=l.split('<tile>',1)[1].split(',');i,x,y=int(a[0]),int(a[3]),int(a[4]);assert 0<=i<len(images)and x>=0 and y>=0 and x+32<=images[i].width and y+32<=images[i].height
  known.add((a[1],int(a[2],16)))
 if l.startswith('<addition>'):adds.append(tuple(l[10:].split(',')))
assert len({a[:4]+a[6:]for a in adds})==len(adds)
assert all((a[0],int(a[1],16))in known and(a[4],int(a[5],16))in known for a in adds)
for p in base.iterdir():
 if p.name not in {'hires.txt','README.txt'}:assert p.read_bytes()==(pack/p.name).read_bytes(),p.name
for n in range(1,1941):
 for ext in ['ram','ppu']:
  f=f'{n:05d}.{ext}';assert (replay/'original/frames'/f).read_bytes()==(replay/'v098/frames'/f).read_bytes(),f
assert int((replay/'v098/home/done').read_text())==1940
assert not re.search(r'\[HDPack\].*(error|Error)|[Ss]cript error|Exception',(replay/'v098/log.txt').read_text())
def heads(n):
 return [(int(x),int(y))for l,x,y,k,p,h,v in (s.split(',')for s in (replay/f'before/tiles/{n:05d}.tiles').read_text().splitlines())if l=='1'and k==HEAD]
components={k for keys in json.loads((ROOT/'validation/v098-build.json').read_text())['native_component_positions'].values()for k in keys}
changed=[];outside=0;count=0
for f in sorted((replay/'v098/frames').glob('*.png')):
 n=int(f.stem);a=np.array(Image.open(replay/'final/frames'/f.name).convert('RGBA'));b=np.array(Image.open(f).convert('RGBA'));assert a.shape==b.shape==(896,1024,4)
 diff=np.any(a!=b,axis=2);allowed=np.zeros((896,1024),bool)
 for frame in [n,max(1,n-1)]:
  for hx,hy in heads(frame):
   x0,x1=max(0,(hx+16)*4),min(1024,(hx+48)*4);y0,y1=max(0,(hy+8)*4),min(896,(hy+40)*4)
   if x0<x1 and y0<y1:allowed[y0:y1,x0:x1]=True
   # Native NES sprites wrap at x=256. Their unwanted left-edge fragments
   # are part of the exhaust correction, and are replaced with transparency.
   for l,x,y,k,p,h,v in(s.split(',')for s in(replay/f'before/tiles/{frame:05d}.tiles').read_text().splitlines()):
    x,y=int(x),int(y)
    if l=='1'and k in components and x<hx and x<32 and 16<=y-hy<=32:
     x0,x1=max(0,x*4),min(1024,(x+8)*4);y0,y1=max(0,(y-8)*4),min(896,y*4)
     if x0<x1 and y0<y1:allowed[y0:y1,x0:x1]=True
 outside+=int((diff&~allowed).sum());count+=1
 if diff.any():changed.append(n)
assert outside==0,outside
report={'version':'0.9.8','recording':'Bionic Commando (USA)(8).mmo','native_frames_checked':1940,'RAM_mismatches':0,'PPU_mismatches':0,'screenshots_compared':count,'changed_pixels_outside_thruster':outside,'prior_rules_preserved':True,'prior_image_assets_unchanged':True,'duplicate_sprite_additions':0,'changed_screenshot_frames':changed,'limits':'Full provided recording replayed; full-run images sampled every three frames. Unrecorded states remain untested.'}
(ROOT/'validation/v098-regression.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='changed_screenshot_frames'},indent=2))
