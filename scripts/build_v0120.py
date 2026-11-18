"""Area 3: painted alpine terrain, pipe works and native creature phases."""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, ctypes, json, re, os
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from build_v0115 import build as previous_build, EAGLE_KEYS
from build_v0111 import cell, fit

ROOT=Path(__file__).resolve().parents[1]
NORMAL='area3&!title&!worldmap&!equipment&!radio&!areaClear&!interception&!interception14'
OUT=NORMAL+'&a3Outside'; INS=NORMAL+'&a3Pipes'

def entries(n):
 return [(int(l),int(x),int(y),k,int(p),int(h),int(v)) for l,x,y,k,p,h,v in (s.split(',')for s in(ROOT/f'capture/area3/{n:05}.tiles').read_text().splitlines())]

def indices(k):
 a=np.unpackbits(np.frombuffer(bytes.fromhex(k),np.uint8)).reshape(16,8);return a[:8]+2*a[8:]

def guard_neighbors(lines, known_lines=()):
 # Same screen-edge fix as Area 2, applied solely to this area's new rules.
 from build_v0112 import guard_area2_neighbors
 # Reuse the reviewed implementation on just the new declarations/rules.
 inherited=[s for s in known_lines if s.startswith('<condition>') and (',spriteNearby,' in s or ',tileNearby,' in s)]
 converted=[s.replace('area3','area2') for s in inherited+lines]
 guarded, report=guard_area2_neighbors(converted)
 return [s.replace('area2','area3').replace('a212Bound','a3120Bound') for s in guarded if s not in inherited],report

def build(dest, reuse=False):
 if not reuse: previous_build(dest)
 else:
  import shutil
  base=ROOT.parent/'output/v0115-extracted'
  for p in dest.iterdir():p.unlink()
  for p in base.iterdir():shutil.copy2(p,dest/p.name)
 lines=(dest/'hires.txt').read_text().splitlines();images=[Image.open(dest/s[5:]).convert('RGBA') for s in lines if s.startswith('<img>')]
 adds=[]
 index=len(images);atlas=Image.new('RGBA',(2048,4096));cells={};rules=[];conds=[];nearby={};covered=set()
 blank=Image.new('RGBA',(32,32));by=defaultdict(list);keyp=defaultdict(set);addby=defaultdict(list)
 for s in lines:
  if '<tile>' in s:
   g,b=s.split('<tile>');a=b.split(',');by[a[1],int(a[2],16)].append((g,a))
  if s.startswith('<addition>'):
   a=s[10:].split(',');addby[a[0],int(a[1],16)].append(a)
 audit=json.loads((ROOT/'capture/area3/audit-before.json').read_text())
 pairs={(r['key'],int(r['palette'],16)) for r in audit};missing={(r['key'],int(r['palette'],16)) for r in audit if r['rule']=='-1'}
 for k,p in sorted(pairs):keyp[k].add(p)
 catalog=json.loads((ROOT/'capture/area3/material-catalog.json').read_text());ids=defaultdict(dict);lookup={}
 for r in catalog:ids[r['layer'],int(r['palette'],16)][r['index']]=r['key'];lookup[r['key'],int(r['palette'],16)]=r
 conds+=['<condition>area3,memoryCheckConstant,004D,==,03','<condition>a3Outside,ppuMemoryCheckConstant,3F00,==,1C','<condition>a3Pipes,ppuMemoryCheckConstant,3F01,==,39']
 def emit(k,p,im,g=NORMAL):
  assert im.size==(32,32),im.size
  b=im.tobytes()
  if b not in cells:
   n=len(cells);xy=n%64*32,n//64*32;assert xy[1]<atlas.height;cells[b]=xy;atlas.paste(im,xy)
  x,y=cells[b];rules.append((f'[{g}]'if g else'')+f'<tile>{index},{k},{p:08X},{x},{y},1,N');covered.add((k,p))
 def near(dx,dy,k,p,kind='sprite'):
  t=kind,dx,dy,k,p
  if t not in nearby:
   name=f'a3120Near{len(nearby)}';nearby[t]=name;conds.append(f'<condition>{name},{kind}Nearby,{dx},{dy},{k},{p:08X},Y')
  return nearby[t]
 def source(a):
  x,y=map(int,a[3:5]);return images[int(a[0])].crop((x,y,x+32,y+32))
 lib=ctypes.CDLL(os.environ.get('BIONIC_XBRZ_LIBRARY',str(ROOT/'tools/scale.so')));lib.scale4.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
 def smoothmask(m):
  a=np.dstack([m.astype('uint8')*255]*4).copy();b=np.zeros((32,32,4),np.uint8);lib.scale4(a.ctypes.data,b.ctypes.data,8,8);return b[:,:,3]/255.
 textures=Image.open(ROOT/'art/area3-materials-v0120.png').convert('RGBA');w,h=textures.size
 tex=[np.array(fit(textures.crop(box),(128,128))) for box in [(0,0,w//2,h//2),(w//2,0,w,h//2),(0,h//2,w//2,h),(w//2,h//2,w,h)]]
 # Use observed tile adjacency to keep material grain continuous across each
 # repeated native block. Shape masks retain collision-facing contours only.
 phases={}
 for n in [1044,1441,1921,2401,2881,3361,3841,4321,4801]:
  es=[e for e in entries(n) if e[0]==0 and e[4]>>24==0x1c and e[3]!='0'*32]
  offsets=Counter(((phases[k][0]-x)%32,(phases[k][1]-y)%32)for _,x,y,k,p,h,v in es if k in phases)
  ox,oy=offsets.most_common(1)[0][0]if offsets else(0,0)
  for _,x,y,k,p,h,v in es:phases.setdefault(k,((x+ox)%32,(y+oy)%32))
 yy,xx=np.mgrid[:32,:32]
 details=Image.open(ROOT/'art/area3-details-v0120.png').convert('RGBA')
 detail=[cell(details,n,main_component=True) for n in range(6)]
 snowledge=fit(detail[3],(128,64))
 def sample(k,t):
  x,y=phases.get(k,(0,0));return tex[t][(yy+y*4)%128,(xx+x*4)%128].copy()
 def outdoor(k,p,i):
  ix=indices(k)
  if not ix.any():return blank
  if p==0x1c302907 and i in [1,2,3,4]:
   x=0 if i in[1,2]else 32;y=0 if i in[1,3]else 32
   return snowledge.crop((x,y,x+32,y+32))
  if p==0x1c201000 and i<70 and i not in range(51,60):return blank # mountains replaced by full distant painting
  if p==0x1c271707 and 9<=i<=40:
   a=sample(k,3);m=smoothmask(ix>0);a[:,:,3]=np.uint8(m*255)
   # Branch cells have horizontal grain; trunk and junction cells stay upright.
   if 21<=i<=36:a[:,:,:3]=np.transpose(a[:,:,:3],(1,0,2))
   return Image.fromarray(a)
  if p==0x1c201000:
   a=sample(k,2 if 51<=i<=59 else 1)
   a[:,:,3]=np.uint8(smoothmask(ix>0)*255) if (ix==0).any() else 255
   return Image.fromarray(a)
  a=sample(k,0);a[:,:,3]=np.uint8(smoothmask(ix>0)*255)
  if p in [0x1c201707,0x1c302907]:
   snow=sample(k,2);m=gaussian_filter(smoothmask(ix==1),1.1)
   if p==0x1c302907:m=np.maximum(m,smoothmask(ix==2)*.72)
   a[:,:,:3]=np.uint8(a[:,:,:3]*(1-m[:,:,None])+snow[:,:,:3]*m[:,:,None])
  return Image.fromarray(a)
 for p in [0x1c271707,0x1c201000,0x1c201707,0x1c302907]:
  for i,k in ids[0,p].items():emit(k,p,outdoor(k,p,i),OUT)
 # Foreground snow lips are native sprites over the same background ledge.
 for k,p in sorted(pairs):
  if p==0xff30290f and (k,0x1c302907) in lookup:emit(k,p,outdoor(k,0x1c302907,lookup[k,0x1c302907]['index']),OUT)
 industry=Image.open(ROOT/'art/area3-industry-v0120.png').convert('RGBA')
 def tight(box):
  a=industry.crop(box);ar=np.array(a);ar[ar[:,:,3]<32,3]=0;a=Image.fromarray(ar);bb=a.getchannel('A').point(lambda x:255 if x>64 else 0).getbbox();return a.crop(bb)
 pipe=tight((170,0,350,630));girder=tight((700,0,840,630));mesh=tight((1040,80,1530,550));bridge=tight((0,740,510,920));lift=tight((520,740,1020,940));spikes=tight((1030,740,1536,920))
 ptex=fit(pipe.crop((0,140,pipe.width,444)),(128,64));gtex=fit(girder.crop((0,30,girder.width,320)),(128,64));mtex=fit(mesh.crop((40,40,mesh.width-40,mesh.height-40)),(64,64));btex=fit(bridge,(128,64))
 itex={};p=0x0f392919
 for y,row in enumerate([[1,3,5,7],[2,4,6,8]]):
  for x,i in enumerate(row):itex[p,i]=ptex.crop((x*32,y*32,x*32+32,y*32+32))
 p=0x0f11020b
 for y,row in enumerate([[2,4,6,8],[3,5,7,9]]):
  for x,i in enumerate(row):itex[p,i]=gtex.crop((x*32,y*32,x*32+32,y*32+32))
 itex[p,1]=mtex.crop((0,0,32,32))
 # Both widths of service column are painted as complete repeating panels.
 narrow=fit(girder.crop((0,30,girder.width,320)),(64,64))
 for y,row in enumerate([[10,12],[11,13]]):
  for x,i in enumerate(row):itex[0x0f11020b,i]=narrow.crop((x*32,y*32,x*32+32,y*32+32))
 for y,row in enumerate([[28,29,30,31],[34,35,36,37]]):
  for x,i in enumerate(row):itex[0x0f11020b,i]=gtex.crop((x*32,y*32,x*32+32,y*32+32))
 smallbridge=fit(bridge,(64,64))
 for y,row in enumerate([[28,29],[30,31]]):
  for x,i in enumerate(row):itex[0x0f392919,i]=smallbridge.crop((x*32,y*32,x*32+32,y*32+32))
 # Wall grilles retain their border, rather than displaying the native mesh
 # silhouette as disconnected blue bars.
 framed=fit(mesh,(256,128))
 panelxy={88:(0,0),87:(224,0),90:(0,96),71:(224,96),89:(0,32),75:(224,32)}
 for i in [84,85,86]:panelxy[i]=(96,0)
 for i in [68,69,70]:panelxy[i]=(96,96)
 for i in [72,73,74]:panelxy[i]=(96,32)
 for i,(x,y)in panelxy.items():itex[0x0f11020b,i]=framed.crop((x,y,x+32,y+32))
 # Full doorway slices keep the radio and goal frames consistent. The goal
 # plaque is applied only to its two distinct eagle-pattern cells below.
 portal=fit(detail[5],(128,160))
 head=fit(detail[5].crop((0,0,detail[5].width,round(detail[5].height*.12))),(128,32))
 for i,x in [(91,96),(96,0),(37,0),(40,96)]:itex[0x0f11020b,i]=head.crop((x,0,x+32,32))
 for i,x in [(38,32),(39,64)]:itex[0x0f11020b,i]=head.crop((x,0,x+32,32))
 for i,x in [(46,0),(16,0),(47,96),(21,96)]:itex[0x0f11020b,i]=portal.crop((x,64,x+32,96))
 for i in [93,95]:itex[0x0f11020b,i]=Image.new('RGBA',(32,32),(5,9,12,255))
 horizontal=fit(girder.transpose(Image.Transpose.ROTATE_90),(128,64))
 for y,row in enumerate([[42,43,44,45],[48,49,50,51]]):
  for x,i in enumerate(row):itex[0x0f11020b,i]=horizontal.crop((x*32,y*32,x*32+32,y*32+32))
 # Slot/rung motifs are background machinery. Replace whole painted panels,
 # avoiding enlarged NES cutouts punched through a new texture.
 for i in [14,19,20,26,27,41,76,77,78,79,80,81,82,83]:
  itex[0x0f11020b,i]=gtex.crop((32,0,64,32))
 for i in [15,17,18,38,39,40]:
  itex[0x0f11020b,i]=head.crop(((i%4)*32,0,(i%4+1)*32,32))
 # Repeated horizontal bridge includes the native narrow end/cap fragments.
 for y,row in enumerate([[32,33,34,35],[36,37,38,39]]):
  for x,i in enumerate(row):itex[0x0f392919,i]=btex.crop((x*32,y*32,x*32+32,y*32+32))
 narrowpipe=fit(pipe.crop((0,140,pipe.width,444)),(64,64))
 for y,row in enumerate([[62,63],[66,67]]):
  for x,i in enumerate(row):itex[0x0f392919,i]=narrowpipe.crop((x*32,y*32,x*32+32,y*32+32))
 # Full pipe-column variants are chosen from matching native shapes, retaining
 # their painting under the red hazard palette and background blue variants.
 keyim={ids[0,p][i]:im for (p,i),im in itex.items() if i in ids[0,p]}
 def machinery(k,p,i):
  ix=indices(k)
  if not ix.any():return blank
  if (p,i)in itex:return itex[p,i]
  if k in keyim:return keyim[k]
  # Modular rail/duct variants use the painted pipe/girder face in the native
  # silhouette; structural corners and caps remain precisely aligned.
  t=ptex if p==0x0f392919 else gtex
  a=np.array(t.crop((32,0,64,32)))
  if p==0x0f392919:
   # Interactive olive pipe contours retain the original external boundary.
   a[:,:,3]=np.uint8(smoothmask(ix>0)*255)
  else:
   # Recessed blue/gray service panels carry continuous painted metal.
   a[:,:,3]=255
  return Image.fromarray(a)
 for p in [0x0f392919,0x0f11020b,0x0f10000a,0x0f271505]:
  for i,k in ids[0,p].items():emit(k,p,machinery(k,p,i),INS)
 # Spike crowns retain two native cells / two spikes per 16 px repeat.
 tip=fit(spikes.crop((0,0,round(spikes.width/8*2),spikes.height)),(64,64))
 for i in [0,1]:itex[0x0f271505,i]=tip.crop((i*32,0,i*32+32,32))
 for x,i in enumerate([6,7]):itex[0x0f271505,i]=tip.crop((x*32,32,x*32+32,64))
 # Whole opaque industrial doorway: the native opening is an interior, never
 # a sky window. Eagle cells are restored separately at the end.
 structs=Image.open(ROOT/'art/area2-structures-v0111.png').convert('RGBA');door=fit(cell(structs,1,main_component=True),(128,192))
 # Reuse existing painted door, grilles, crates and machinery by native key
 # before generic rail fragments, without importing another area's guards.
 overrides=[(ids[0,p][i],p,im,INS) for (p,i),im in itex.items()]
 for p in [0x0f392919,0x0f11020b,0x0f10000a,0x0f271505]:
  for i,k in ids[0,p].items():
   if (p,i)in itex or k=='0'*32:continue
   choices=[(pp,g,a)for(kk,pp),items in by.items()if kk==k and pp>>24==15 for g,a in items if ('area2' in g or 'area5' in g or 'area4' in g) and not any(t in g for t in ['Near','Bound','areaClear','radio','worldmap','equipment','interception'])]
   if choices:
    pp,g,a=choices[0];overrides.append((k,p,source(a),INS))
 # New solid wall base keeps original transparent black background as a dark
 # factory interior. Outdoor panorama is the already approved alpine art.
 Image.new('RGBA',(1024,960),(9,17,23,255)).save(dest/'area3-interior-back.png')
 backgrounds=[f'[{OUT}&screenEnabled]<background>area13-distance.png,1,0,0,1',f'[{INS}&screenEnabled]<background>area3-interior-back.png,1,0,0,1']
 # Original mobile platform is a 32x16 mirrored metasprite.
 platform=fit(lift,(128,64))
 for l,x,y,k,p,h,v in entries(5401):
  if l!=1 or p!=0xff30210f:continue
  im=platform.crop(((x-96)*4,(y-162)*4,(x-88)*4,(y-154)*4))
  if h:im=ImageOps.mirror(im)
  emit(k,p,im,INS+('&hmirror'if h else'&!hmirror'))
 # Paint complete native creature assemblies; each native pose selects its
 # own leg/wing/jaw frame. No timer substitutes for the game's animation.
 rs=json.loads((ROOT/'capture/area3/assemblies.json').read_text());creatures=Image.open(ROOT/'art/area3-creatures-v0120.png').convert('RGBA')
 art=[]
 for row,(y0,y1) in enumerate([(0,380),(380,680),(680,1024)]):
  for col in range(3):
   im=creatures.crop((col*512,y0,(col+1)*512,y1));ar=np.array(im);ar[ar[:,:,3]<32,3]=0;im=Image.fromarray(ar);box=im.getchannel('A').point(lambda x:255 if x>64 else 0).getbbox();art.append(im.crop(box))
 effects=Image.open(ROOT/'art/area2-effects-v0111.png').convert('RGBA');burst=cell(effects,0,main_component=True);smoke=cell(effects,2,main_component=True)
 specs=[(0,art[0]),(8,art[1]),(9,art[2]),(1,art[4]),(3,art[5]),(2,art[3]),(4,ImageOps.mirror(art[3])),(5,art[6]),(12,art[8]),(13,smoke),(14,burst),(16,smoke),(20,burst)]
 fallbacks={};pose_count=0
 for num,painting in specs:
  rec=rs[num];ww,hh=rec['size'];parts=rec['parts'];mask=Image.new('L',(ww,hh))
  for x,y,k,p,h,v in parts:
   t=Image.fromarray(np.uint8(indices(k)>0)*255)
   if h:t=ImageOps.mirror(t)
   if v:t=ImageOps.flip(t)
   mask.paste(t,(x,y),t)
  bb=mask.getbbox();canvas=Image.new('RGBA',(ww*4,hh*4));canvas.alpha_composite(fit(painting,((bb[2]-bb[0])*4,(bb[3]-bb[1])*4)),(bb[0]*4,bb[1]*4))
  preview=ROOT/'validation/pose-previews/area3';preview.mkdir(parents=True,exist_ok=True);canvas.save(preview/f'{num:02}.png')
  # All parts form a positive signature. Use two distinctive cells nearest
  # each tile; fallbacks cover partial clipping without one-past-screen reads.
  signature=sorted(parts,key=lambda t:(sum(1 for rr in rs[:15] if any(z[2]==t[2]for z in rr['parts'])),t[1],t[0]))[:3]
  for x,y,k,p,h,v in parts:
   im=canvas.crop((x*4,y*4,(x+8)*4,(y+8)*4))
   if h:im=ImageOps.mirror(im)
   if v:im=ImageOps.flip(im)
   for pp in sorted(keyp[k]):
    if pp>>24!=255:continue
    guard=OUT+('&hmirror'if h else'&!hmirror')+('&vmirror'if v else'&!vmirror')
    terms=[near((ax-x)*(-1 if h else 1),(ay-y)*(-1 if v else 1),ak,pp)for ax,ay,ak,ap,ah,av in signature if (ax,ay)!=(x,y)]
    emit(k,pp,im,guard+('&'+'&'.join(terms)if terms else''))
    fallbacks.setdefault((k,pp,h,v),im)
  pose_count+=1
 for (k,p,h,v),im in fallbacks.items():emit(k,p,im,NORMAL+('&hmirror'if h else'&!hmirror')+('&vmirror'if v else'&!vmirror'))
 for (k,p,h,v),im in fallbacks.items():emit(k,p,im,NORMAL)
 # Split lower plant jaw cells use half of the fully open painting. A closed
 # upper bud uses its own full assembly above, preserving the original timing.
 openplant=fit(detail[0],(256,32))
 for num in [10,11]:
  rec=rs[num]
  for x,y,k,p,h,v in rec['parts']:
   im=openplant.crop((x*4+(160 if num==10 else 0),0,x*4+(192 if num==10 else 32),32))
   if h:im=ImageOps.mirror(im)
   for pp in sorted(keyp[k]):
    if pp>>24==255:emit(k,pp,im,OUT+('&hmirror'if h else'&!hmirror'))
 # The two mobile seed projectiles remain separate from the plant jaw.
 for k,seed in [('0673F8FCFC7D39920000000000000000',detail[1]),('0062F0F0300301000000000000000000',detail[2])]:
  for p in sorted(keyp[k]):emit(k,p,fit(seed,(32,32)),OUT)
 # Four foreground ledge fragments use the same painted snow material.
 for k in ['0301000000000000B06E6D454D080800','1824220200000000E69915746E6A4A88','83CF79DFEF7BA6035C108620108418FC','83D7FAFCF2E150085C2801010D122DF3']:
  emit(k,0xff30290f,outdoor(k,0x1c302907,99),OUT)
 # Live communicator inventory icon, on both the map and equipment screen.
 comm=Image.open(ROOT/'art/area3-communicator-v0120.png').convert('RGBA')
 comm=fit(comm.crop(comm.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()),(64,64))
 commkeys=[['0D00181111C080000000060F0F3F7FFF','C0201804042222220000000000E0E0E0'],['E10101010101011FFF1F1F1F1F1F1F1F','C12121212121121CC000000000000000']]
 for y,row in enumerate(commkeys):
  for x,k in enumerate(row):
   for g in ['area3&equipment','area3&worldmap']:emit(k,0xff30260f,comm.crop((x*32,y*32,x*32+32,y*32+32)),g)
 # Guards in the radio room use three real native walking phases, including
 # their observed one-pixel leg offsets and damage palettes.
 from poses import make_actor
 import tempfile,shutil
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td)
  for sub in ['capture','art','validation']:(tmp/sub).mkdir()
  shutil.copy2(ROOT/'capture/area3/guard-poses.json',tmp/'capture/a13trooper-poses.json')
  shutil.copy2(ROOT/'capture/spencer-poses.json',tmp/'capture/spencer-poses.json')
  for p in(ROOT/'art').glob('*.png'):(tmp/'art'/p.name).symlink_to(p)
  pending=[]
  c,a,v=make_actor(tmp,pairs,lambda k,p,im,g=None:pending.append((k,p,im,g)),blank,'a13trooper',1,0xff36150f)
  names={line.split(',')[0][11:]:'a3120_'+line.split(',')[0][11:] for line in c}
  def rename(st):return re.sub(r'[A-Za-z_][A-Za-z0-9_-]*',lambda m:names.get(m.group(),m.group()),st)
  conds.extend(map(rename,c));adds.extend(a)
  existing_positions={tuple(z[:4]+z[6:]):z[4] for values in addby.values() for z in values}
  actual_virtual={}
  for line in a:
   z=line[10:].split(',');actual_virtual[z[4],int(z[5],16)]=existing_positions.get(tuple(z[:4]+z[6:]),z[4])
  for k,p,im,g in pending:emit(actual_virtual.get((k,p),k),p,im,NORMAL+('&'+rename(g)if g else''))
  for k,p in v:
   k=actual_virtual.get((k,p),k)
   if (k,p)not in by:emit(k,p,blank,None)
  shutil.copy2(tmp/'validation/a13trooper_pose_mapping.json',ROOT/'validation/v0120-guards.json')
  shutil.copytree(tmp/'validation/pose-previews/a13trooper',ROOT/'validation/pose-previews/area3-guards',dirs_exist_ok=True)
 # Paint previously known sprite fragments in their additional observed
 # palette; retain pose, weapon, facing and flash selection conditions.
 aliases=0;pending_alias=[]
 fadepairs={(k,p)for k,p in missing if p in [0xff000a0f,0xff0f0f0f,0xff101a0f]}
 for k,p in sorted((missing-covered)|fadepairs):
  if p>>24!=255:continue
  choices=[(pp,items)for(kk,pp),items in by.items()if kk==k and pp>>24==255]
  if not choices:continue
  pp,items=min(choices,key=lambda v:sum(((v[0]>>s)&255)!=((p>>s)&255)for s in[16,8,0]))
  for g,a in items:
   terms=g.strip('[]').split('&') if g else[]
   if any(re.fullmatch(r'area\d+',t) for t in terms):continue
   im=source(a)
   if (k,p)in fadepairs:
    aa=np.array(im);aa[:,:,:3]=np.uint8(aa[:,:,:3]*{0xff101a0f:.62,0xff000a0f:.32,0xff0f0f0f:0}[p]);im=Image.fromarray(aa)
   emit(k,p,im,'area3&'+g.strip('[]')if g else'area3')
  # Ensure clipped fragment fallback uses the last painted native fragment.
  generic=[a for g,a in items if not g or g=='[!title]']
  if generic:
   im=source(generic[-1])
   if (k,p)in fadepairs:
    aa=np.array(im);aa[:,:,:3]=np.uint8(aa[:,:,:3]*{0xff101a0f:.62,0xff000a0f:.32,0xff0f0f0f:0}[p]);im=Image.fromarray(aa)
   emit(k,p,im,'area3&!title')
  aliases+=1
 # End-screen number uses the approved debrief font and original live text.
 for x,ch in [(72,'0'),(80,'3')]:
  k=next(e[3]for e in entries(10560)if e[0]==0 and e[1]==x and e[2]==40)
  im=Image.new('RGBA',(32,32));ImageDraw.Draw(im).text((16,16),ch,anchor='mm',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',29),fill=(233,231,211))
  emit(k,0x0f200f0f,im,'area3&areaClear')
 im=Image.new('RGBA',(32,32));ImageDraw.Draw(im).text((16,16),'F',anchor='mm',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',29),fill=(233,231,211))
 emit('FEC0C0FCC0C0C0000000000000000000',0x0f200f0f,im,'area3&areaClear')
 # Emblem stays recognizable for the Area 3 goal-door palette. Ordinary
 # radio headers have distinct keys and receive no eagle.
 plaque=Image.open(dest/'boss-door-eagle-v0115.png').convert('RGBA')
 for col,k in enumerate(EAGLE_KEYS):
  for p in sorted(keyp[k]):
   if p>>24!=255:overrides.append((k,p,plaque.crop((col*32,0,col*32+32,32)),NORMAL))
 # The earlier control-room sample had OAM covering this elbow. Its native
 # fragments were therefore never sampled into the painted reference map.
 control=fit(Image.open(ROOT/'art/control-reference.png').convert('RGBA'),(1024,960))
 for l,x,y,k,p,h,v in entries(7201):
  if l==0 and p==0x0f2b1b0b and 64<=x<80 and 160<=y<192:
   overrides.append((k,p,control.crop((x*4,y*4,(x+8)*4,(y+8)*4)),NORMAL))
 # Reorder detailed architecture before material fallbacks.
 old_rules=rules;rules=[]
 for k,p,im,g in overrides:emit(k,p,im,g)
 rules+=old_rules
 new,guards=guard_neighbors(conds+list(dict.fromkeys(rules)),lines)
 at=next(i for i,s in enumerate(lines)if '<tile>'in s)
 declarations=[s for s in new if s.startswith('<condition>')]
 tilerules=[s for s in new if not s.startswith('<condition>')]
 existing_adds={tuple(a[:4]+a[6:]) for values in addby.values() for a in values}
 unique_adds=[]
 for s in adds:
  a=s[10:].split(',');identity=tuple(a[:4]+a[6:])
  if identity not in existing_adds:unique_adds.append(s);existing_adds.add(identity)
 lines[at:at]=['<img>area3-v0120.png']+declarations+unique_adds+backgrounds+tilerules
 lines[0]='# Bionic Commando HD v0.12.0 - Area 3 alpine approach and pipe works'
 (dest/'hires.txt').write_text('\n'.join(lines)+'\n');atlas.crop((0,0,2048,max(32,((len(cells)+63)//64)*32))).save(dest/'area3-v0120.png')
 readme=(dest/'README.txt').read_text().replace('v0.11.5','v0.12.0').replace('Area 2 review build','Area 3 review build')
 readme=readme.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nArea 3 painted snow, alpine cliffs, tree branches, industrial pipes,\nplatforms and spikes. Native crawling, flying and plant-mouth phases\nuse painted creatures. Goal door eagle and AREA 03 CLEAR lettering.\n\n',1);(dest/'README.txt').write_text(readme)
 report={'version':'0.12.0','new_rules':len(set(rules)),'atlas_cells':len(cells),'creature_poses':pose_count,'aliases':aliases,'bounds':guards,'remaining_initial_pairs':[(k,f'{p:08X}')for k,p in sorted(missing-covered)]}
 (ROOT/'validation/v0120-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'pack');ap.add_argument('--reuse-approved',action='store_true');a=ap.parse_args();build(a.output,a.reuse_approved)

if __name__=='__main__':main()
