"""Area 2 artwork over the immutable approved v0.10.6 runtime."""
from pathlib import Path
from collections import defaultdict
import argparse,ctypes,hashlib,json,re,shutil,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy.ndimage import distance_transform_edt,gaussian_filter
from runtime_baseline import copy_baseline
ROOT=Path(__file__).resolve().parents[1]
NORMAL='area2&!interception&!interception14&!title&!worldmap&!equipment&!radio&!areaClear'
def indices(k):
 a=np.unpackbits(np.frombuffer(bytes.fromhex(k),dtype=np.uint8)).reshape(16,8);return a[:8]+2*a[8:]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'pack');args=ap.parse_args();build(args.output)
def build(dest):
 base=ROOT/'baselines/v0106';copy_baseline(base,dest,'0106')
 lines=(base/'hires.txt').read_text().splitlines();images=[Image.open(base/l[5:]).convert('RGBA')for l in lines if l.startswith('<img>')]
 atlas=Image.new('RGBA',(2048,4096));cells={};rules=[];conditions=['<condition>area2,memoryCheckConstant,004D,==,02','<condition>a2Cave,ppuMemoryCheckConstant,3F01,==,2B','<condition>a2Outside,ppuMemoryCheckConstant,3F0D,==,30'];adds=[];backgrounds=[];blank=Image.new('RGBA',(32,32));idx=len(images)
 def emit(k,p,im,guard=NORMAL):
  assert im.size==(32,32)
  data=im.tobytes()
  if data not in cells:
   n=len(cells);xy=n%64*32,n//64*32;assert xy[1]<atlas.height;cells[data]=xy;atlas.paste(im,xy)
  x,y=cells[data];rules.append((f'[{guard}]'if guard else'')+f'<tile>{idx},{k},{p:08X},{x},{y},1,N')
 def source(a):
  x,y=map(int,a[3:5]);return images[int(a[0])].crop((x,y,x+32,y+32))
 by=defaultdict(list);keyp=defaultdict(set)
 for l in lines:
  if '<tile>'in l:
   g,b=l.split('<tile>');a=b.split(',');by[a[1],int(a[2],16)].append((g,a));keyp[a[1]].add(int(a[2],16))
 audit=json.loads((ROOT/'capture/area2/audit-before.json').read_text());allpairs={(r['key'],int(r['palette'],16))for r in audit};missing={(r['key'],int(r['palette'],16))for r in audit if r['rule']=='-1'}
 catalog=json.loads((ROOT/'capture/area2/material-catalog.json').read_text());groups=defaultdict(dict)
 for e in catalog:groups[e['layer'],int(e['palette'],16)][e['index']]=e['key']
 def keys(p,ns):return{groups[0,p][n]for n in ns if n in groups[0,p]}
 roof=keys(0x0F212A1A,[1,2,3,4,17,18,19,20,21,22,23,24]);rocks=keys(0x0F201000,range(20));spikes=keys(0x0F201000,[27,29,39,40]);platforms=keys(0x0F281808,[0,1,2,3,4,5,6,7,8,9,10,11,14,15])
 bricks=keys(0x0F2B1C0B,[0,1,2,3,4,5,6,7,10,11,12,13,14,15,69,77,78,85,107,108,109,127])
 water=keys(0x0F2B1C0B,[8,9,16,17,26,27,28,29,30,31,32,33,41,42,71,72,73,99,103])-rocks
 sheet=Image.open(ROOT/'art/area2-materials-v0110.png').convert('RGBA');w,h=sheet.size
 textures={'rock':sheet.crop((0,0,w//2,h//2)).resize((128,128),Image.Resampling.LANCZOS),'brick':sheet.crop((w//2,0,w,h//2)).resize((128,128),Image.Resampling.LANCZOS),'moss':sheet.crop((0,round(h*.65),w//2,round(h*.79))).resize((128,64),Image.Resampling.LANCZOS),'water':sheet.crop((w//2,h//2,w,h)).resize((128,128),Image.Resampling.LANCZOS)}
 rockph=json.loads((ROOT/'capture/area2/rock-phases.json').read_text())
 library=ctypes.CDLL(os.environ.get('BIONIC_XBRZ_LIBRARY',str(ROOT/'tools/scale.so')));library.scale4.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
 def scale(im):
  a=np.array(im.convert('RGBA'))[:,:,[2,1,0,3]].copy();hh,ww=a.shape[:2];b=np.zeros((hh*4,ww*4,4),dtype=np.uint8);library.scale4(a.ctypes.data,b.ctypes.data,ww,hh);return Image.fromarray(b[:,:,[2,1,0,3]])
 def mask(ix):return np.array(scale(Image.fromarray(np.repeat((ix>0)[:,:,None],4,axis=2).astype('uint8')*255)))[:,:,3]/255.
 def material(k,p,kind):
  ix=indices(k);m=mask(ix);a=np.zeros((32,32,4),dtype=np.uint8)
  if not m.any():return blank
  seed=int(k[:8],16);yy,xx=np.mgrid[:32,:32]
  if kind in ['rock','brick','moss','water']:
   t=np.array(textures[kind]);th,tw=t.shape[:2];ox=(seed%4)*32%tw;oy=((seed//7)%4)*32%th
   rgb=t[(yy+oy)%th,(xx+ox)%tw,:3].astype(float)
   native=np.repeat(np.repeat(ix,4,0),4,1)
   if kind=='rock':
    rt=np.array(textures['rock'].resize((64,64),Image.Resampling.LANCZOS));rx,ry=rockph.get(k,(0,0));rgb=rt[(yy+ry*4)%64,(xx+rx*4)%64,:3].astype(float)*1.14
    if p==0x0F372717:rgb*=np.array([1.25,.92,.58]);m[:]=1
   if kind=='brick':rgb*=.83;m[:]=1
   if kind=='water':
    rgb*=gaussian_filter(np.choose(native,[.42,.64,.92,1.06]),2)[:,:,None];m[:]=1
   if kind=='moss':
    rgb=t[np.minimum(yy,th-1),(xx+ox)%tw,:3].astype(float);rgb*=.85+gaussian_filter((native==1).astype(float),2)[:,:,None]*.15
   if kind=='rock'and np.sum(ix==0)<16:m[:]=1
  elif kind=='spike':
   native=np.repeat(np.repeat(ix,4,0),4,1);rgb=np.zeros((32,32,3));rgb[:]=[124,151,161];rgb+=((31-xx)*2.8)[:,:,None];rgb[native==1]=[226,237,240]
  else:
   if kind=='stucco':cols=np.array([[0,0,0],[226,225,211],[136,151,145],[125,83,41]],float)
   elif kind=='grass':cols=np.array([[0,0,0],[172,187,104],[86,113,48],[45,65,31]],float)
   elif kind=='roof':cols=np.array([[0,0,0],[169,190,131],[66,106,65],[24,50,39]],float)
   elif kind=='spray':cols=np.array([[0,0,0],[211,245,245],[53,165,178],[18,71,80]],float)
   else:cols=np.array([[0,0,0],[32,55,51],[74,118,112],[166,202,186]],float)
   weights=[]
   for c in range(4):weights.append(np.array(scale(Image.fromarray(np.dstack([np.uint8(ix==c)*255]*3+[np.full((8,8),255,dtype=np.uint8)]))))[:,:,0]/255.)
   weights=np.stack(weights,2);weights/=np.maximum(weights.sum(2,keepdims=True),1e-6);rgb=weights@cols
   texture=np.array(textures['rock'])[:32,:32,:3].mean(2);rgb+=(texture-texture.mean())[:,:,None]*.35
   dist=gaussian_filter(distance_transform_edt(np.pad(m>0,4,mode='edge'))[4:-4,4:-4],1);gy,gx=np.gradient(dist);rgb+=np.clip((-gx-gy)*7,-20,20)[:,:,None]
  if kind=='roof':m=np.array(scale(Image.fromarray(np.repeat((ix!=1)[:,:,None],4,axis=2).astype('uint8')*255)))[:,:,3]/255.
  if kind=='stucco':m[:]=1
  a[:,:,:3]=np.clip(rgb,0,255).astype('uint8');a[:,:,3]=np.uint8(m*255)
  return Image.fromarray(a)
 for k,p in sorted(allpairs):
  if p>>24==255:continue
  kind=None
  if p==0x0F302111 or(p==0x0F212A1A and k not in roof):emit(k,p,blank,NORMAL+'&a2Outside');continue
  if p==0x0F212A1A:kind='roof'
  if p==0x0F201017:kind='stucco'
  if p==0x0F372717:kind='rock'
  if p in [0x0F201000,0x0F2B1C0B,0x0F281808,0x0F271606]:
   kind='metal'
   if k in rocks:kind='rock'
   elif k in spikes:kind='spike'
   elif k in platforms:kind='moss'
   elif k in bricks:kind='brick'
   elif k in water:kind='water'
   elif p==0x0F281808:kind='metal'
   if p==0x0F201000 and k not in rocks|spikes|platforms:kind='stucco'
  if kind:
   guard=NORMAL+('&a2Outside'if p in[0x0F201017,0x0F372717,0x0F212A1A]else'&a2Cave')
   emit(k,p,material(k,p,kind),guard)
 # A dark aqueduct void replaces the unrelated outdoor sky behind apertures.
 Image.new('RGBA',(1024,960),(7,16,20,255)).save(dest/'area2-cave-back.png')
 backgrounds += [f'[{NORMAL}&a2Cave&screenEnabled]<background>area2-cave-back.png,1,0,0,1',f'[{NORMAL}&a2Outside&screenEnabled]<background>area13-distance.png,1,0,0,1']
 # The native 02 stays live; only its font changes to the existing debrief font.
 es=[l.split(',')for l in(ROOT/'capture/area2/11520.tiles').read_text().splitlines()]
 for x,ch in [(72,'0'),(80,'2')]:
  key=next(e[3]for e in es if e[0]=='0'and int(e[1])==x and int(e[2])==40)
  im=Image.new('RGBA',(32,32));ImageDraw.Draw(im).text((16,16),ch,anchor='mm',font=ImageFont.truetype(os.environ.get('BIONIC_MONO_FONT','/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'),29),fill=(233,231,211))
  emit(key,0x0F200F0F,im,'area2&areaClear')
  if ch=='2':emit(key,0x0F201000,im,'area2&!worldmap&!equipment&!title')
 # Sprite and remaining rare state repairs are generated from recorded parts.
 from area2_actors_v0110 import patch_actors
 stats=patch_actors(ROOT,allpairs,missing,lines,images,emit,conditions,adds,material,blank,NORMAL)
 unique=list(dict.fromkeys(rules));at=next(i for i,l in enumerate(lines)if '<tile>'in l)
 lines[at:at]=[f'<img>area2-v0110.png']+conditions+list(dict.fromkeys(adds))+backgrounds+unique
 lines[0]='# Bionic Commando HD v0.11.0 - Area 2 aqueduct and recorded state coverage'
 (dest/'hires.txt').write_text('\n'.join(lines)+'\n');atlas.crop((0,0,2048,max(32,((len(cells)+63)//64)*32))).save(dest/'area2-v0110.png')
 (dest/'README.txt').write_text("BIONIC COMMANDO HD — v0.11.0\nArea 2 review build\n\nNEW IN THIS BUILD\nPainted aqueduct rock and masonry, mossy platforms, animated water and\nvisible steel spike tips. Updated tracked carrier and hanging hazard;\nconsistent red grenadier running/throwing and crouching rifleman artwork.\nCorrect AREA 02 CLEAR lettering and paused-map weapon icon.\n\nThe pit's spike tips also sit at the bottom of the original game's view and\ncan scroll below the screen. Original geometry, collision, camera, damage\nand animation timing are retained.\n\nIncludes the approved v0.10.6 graphics for the intro, Area 1, Area 13,\nArea 4, Area 5, Area 15, Area 16 and overhead encounters. White, green and\nred town characters retain their matching dialogue portraits.\n\nINSTALL\nLoad Bionic Commando (USA).nes in Mesen/MesenCE.\nChoose Tools > HD Packs (NES) > Install HD Pack, select this ZIP,\nconfirm installation, enable HD packs in NES video settings, and reload.\n\nManual install: keep hires.txt and all PNGs together in\n  HdPacks/Bionic Commando (USA)/\nThe directory name must match the ROM filename without .nes.\n\nREVIEW SCOPE\nSupplied recordings and their observed graphics states. Later areas,\nunrecorded states and unrecorded weapons still need review.\nThis is a work-in-progress review build, not a finished-game release.\n\nNo gameplay, controls, music, level geometry or ROM modifications.\nNo ROM, movie recording, emulator or development files are included.\nMesenCE 2.2.1 / Mesen-compatible HD pack format 109, 4x artwork.\nSupported whole-ROM SHA1: D3A4BFD995D18C4A386971631759AECA3A7CFF8D\n")
 (ROOT/'validation/v0110-build.json').write_text(json.dumps({'version':'0.11.0','new_rules':len(unique),'atlas_cells':len(cells),'actors':stats},indent=2)+'\n')
 print('Built Area 2:',len(unique),'rules,',len(cells),'art cells',stats)
if __name__=='__main__':main()
