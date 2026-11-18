"""Native-anchored Area 2 enemies, carrier and animated water sprite states."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,tempfile,shutil
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from poses import make_actor
def patch_actors(root,allpairs,missing,lines,images,emit,conds,adds,material,blank,normal,enemy_records=None):
 def idx(k):
  a=np.unpackbits(np.frombuffer(bytes.fromhex(k),dtype=np.uint8)).reshape(16,8);return a[:8]+2*a[8:]
 keyp=defaultdict(set);by=defaultdict(list)
 for k,p in sorted(allpairs):keyp[k].add(p)
 for line in lines:
  if '<tile>'in line:
   g,s=line.split('<tile>');a=s.split(',');by[a[1],int(a[2],16)].append((g,a))
 covered=set();nearby={}
 def near(x,y,k):
  t=x,y,k
  if t not in nearby:
   name='a2Near'+str(len(nearby));nearby[t]=name;conds.append(f'<condition>{name},spriteNearby,{x},{y},{k},FF36150F,Y')
  return nearby[t]
 def crop(a):
  x,y=map(int,a[3:5]);return images[int(a[0])].crop((x,y,x+32,y+32))
 with tempfile.TemporaryDirectory()as td:
  tmp=Path(td);(tmp/'capture').mkdir();(tmp/'art').mkdir();(tmp/'validation').mkdir()
  shutil.copy2(enemy_records or root/'capture/area2/enemy-poses.json',tmp/'capture/enemy-poses.json')
  shutil.copy2(root/'capture/spencer-poses.json',tmp/'capture/spencer-poses.json')
  for p in(root/'art').glob('*.png'):(tmp/'art'/p.name).symlink_to(p)
  pending=[]
  def record(k,p,im,g=None):pending.append((k,p,im,g));covered.add((k,p))
  c,a,v=make_actor(tmp,allpairs,record,blank,'enemy',3,0xFF36150F)
  names={l.split(',')[0][11:]:'a2_'+l.split(',')[0][11:]for l in c}
  def rename(s):return re.sub(r'[A-Za-z_][A-Za-z0-9_-]*',lambda m:names.get(m.group(),m.group()),s)
  conds.extend(map(rename,c));adds.extend(a)
  for k,p,im,g in pending:emit(k,p,im,normal+('&'+rename(g)if g else''))
  # Virtual fallbacks must be unconditional and transparent outside Area 2.
  for k,p in v:emit(k,p,blank,None)
  shutil.copy2(tmp/'validation/enemy_pose_mapping.json',root/'validation/v0110-enemy-poses.json')
  shutil.copytree(tmp/'validation/pose-previews/enemy',root/'validation/pose-previews/area2',dirs_exist_ok=True)
 # The carrier uses native sprite cells wherever available. Only holes in its
 # native assembly receive an additional cell, attached to its unique driver.
 rec=json.loads((root/'capture/area2/carrier.json').read_text());head=rec['head'];parts=rec['parts'];sheet=Image.open(root/'art/area2-tracked-carrier-v0110.png').convert('RGBA')
 art=sheet.crop(sheet.getchannel('A').point(lambda a:255 if a>64 else 0).getbbox()).resize((224,160),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(384,320));canvas.alpha_composite(art,(0,96));(root/'validation/pose-previews/area2/carrier.png').parent.mkdir(exist_ok=True,parents=True);canvas.save(root/'validation/pose-previews/area2/carrier.png')
 # Two hub states share exactly the same boom, driver and chassis pixels.
 alternate=canvas.copy()
 for cx in [88,135,183]:
  box=(cx-8,226,cx+8,242);hub=canvas.crop(box);rot=hub.rotate(34,Image.Resampling.BICUBIC);mask=Image.new('L',(16,16));ImageDraw.Draw(mask).ellipse((2,2,13,13),fill=255);alternate.paste(rot,box,mask)
 positions=defaultdict(set)
 ball='1436677D657D36140C0E3D3F27270E0C'
 for dx,dy,k,h,v in parts:
  if k==ball or dy not in[0,8,16,24,32]:continue
  positions[k].add((dx,dy,h,v))
 anchor='7F6B3F1F1F18171F5D5D221C00070F1F'
 palettes=sorted(keyp[anchor]);carrierkeys=set(positions)
 phase='FCFEFFFFCFFFFEFC08FCC6BABBC6FC10'
 for ay in range(-16,24,8):
  for ax in range(-24,40,8):
   dx,dy=ax-16,ay+16
   vk=hashlib.md5(f'area2-carrier-chassis:{ax}:{ay}'.encode()).hexdigest().upper()
   for p in palettes:
    adds.append(f'<addition>{anchor},{p:08X},{ax},{ay},{vk},{p:08X},N')
    box=((40+dx)*4,(24+dy)*4,(48+dx)*4,(32+dy)*4)
    for alt,c in[(True,alternate),(False,canvas)]:
     im=c.crop(box);guard=normal
     if alt:guard+='&'+near(-32-dx,32-dy,phase)
     emit(vk,p,im,guard)
    emit(vk,p,blank,None)
 for k,poss in positions.items():
  for dx,dy,h,v in sorted(poss):
   guard=normal+'&'+near((-16-dx)*(-1 if h else 1),(16-dy)*(-1 if v else 1),anchor)
   for p in sorted(keyp[k]):emit(k,p,blank,guard);covered.add((k,p))
  # Painted native fragments survive clipping and the original breakup motion.
  for h in[0,1]:
   same=[t for t in sorted(poss)if t[2]==h]
   if not same:continue
   dx,dy,hh,v=same[0]
   im=canvas.crop(((40+dx)*4,(24+dy)*4,(48+dx)*4,(32+dy)*4))
   if h:im=ImageOps.mirror(im)
   if v:im=ImageOps.flip(im)
   for p in sorted(keyp[k]):emit(k,p,im,normal+('&hmirror'if h else'&!hmirror'))
  dx,dy,h,v=sorted(poss)[0];im=canvas.crop(((40+dx)*4,(24+dy)*4,(48+dx)*4,(32+dy)*4))
  if h:im=ImageOps.mirror(im)
  if v:im=ImageOps.flip(im)
  for p in sorted(keyp[k]):emit(k,p,im,normal)
 # The independently moving hanging weight retains its native position.
 ballart=Image.new('RGBA',(32,32));d=ImageDraw.Draw(ballart)
 d.ellipse((3,3,29,30),fill=(37,55,57),outline=(153,181,181),width=3)
 d.ellipse((7,6,22,21),fill=(85,113,113),outline=(192,210,205),width=2)
 d.ellipse((12,11,22,23),fill=(30,46,48));d.line((15,0,15,4),fill=(186,202,198),width=3)
 for p in sorted(keyp[ball]):emit(ball,p,ballart,normal);covered.add((ball,p))
 chain=Image.new('RGBA',(32,32));d=ImageDraw.Draw(chain);d.ellipse((9,0,23,31),fill=(23,31,34),outline=(166,185,189),width=4);d.ellipse((13,5,19,25),fill=(0,0,0,0));d.line((11,7,11,23),fill=(221,231,231),width=2)
 for p in sorted(keyp[rec['chain']]):emit(rec['chain'],p,chain,normal);covered.add((rec['chain'],p))
 # Preserve complete painted mappings when a familiar part gets a new palette.
 aliases=0
 for k,p in sorted(missing-covered):
  if p>>24!=255:continue
  candidates=[(pp,items)for(kk,pp),items in by.items()if kk==k and pp>>24==255]
  if candidates:
   pp,items=min(candidates,key=lambda t:sum(((p>>s)&255)!=((t[0]>>s)&255)for s in[16,8,0]))
   for g,a in items:
    guard=normal+('&'+g[1:-1]if g else'');emit(k,p,crop(a),guard)
   emit(k,p,material(k,p,'spray'if p==0xFF302C0F else'metal'),normal)
   aliases+=1;covered.add((k,p))
 # Paused world-map inventory uses the same four painted weapon cells.
 for(k,p),items in by.items():
  if(k,p)not in allpairs:continue
  for g,a in items:
   if g=='[equipment]'and k in {'00060D1A346FDFA7000203060C1B3EE4','023C1C2E03219EC01D1B2F173F7FFE40','47071D3E4C844A3446031B0E34FC7E37','60F0F87830100810E0908858381818F0'}:
    emit(k,p,crop(a),'area2&worldmap')
 # Native fluid and fragment masks retain their shape and original phase.
 for k,p in sorted(missing-covered):
  if p>>24!=255:continue
  kind='spray'if p==0xFF302C0F else'metal'
  im=material(k,p,kind);emit(k,p,im,normal);covered.add((k,p))
 # Remaining reactor and radio edge patterns get the matching nearby palette's
 # painted source; no condition from another area is imported.
 for k,p in sorted(missing):
  if p>>24==255 or p in[0x0F302111,0x0F212A1A,0x0F201017,0x0F372717,0x0F201000,0x0F2B1C0B,0x0F281808,0x0F271606,0x0F200F0F]:continue
  choices=[(pp,a)for(kk,pp),items in by.items()if kk==k and pp>>24==15 for g,a in items if not g or all(s not in g for s in ['area13','area4','area5','area16','worldmap','title','equipment','areaClear'])]
  if choices:
   pp,a=min(choices,key=lambda t:sum(((p>>s)&255)!=((t[0]>>s)&255)for s in[16,8,0]));emit(k,p,crop(a),'area2&!worldmap&!equipment&!title&!areaClear')
  else:emit(k,p,material(k,p,'metal'),'area2&!worldmap&!equipment&!title&!areaClear')
 return {'native_carrier_keys':len(carrierkeys),'new_enemy_poses':len(json.loads((root/'capture/area2/enemy-poses.json').read_text())),'new_palette_aliases':aliases}
