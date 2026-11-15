"""Area 13 artwork, scoped to observed area state; no game-state writes."""
import json,hashlib
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import map_coordinates
from poses import make_actor

def entries(root,n):
 return [(int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6]))for a in (l.split(',')for l in (root/f'capture/area13/{n:05}.tiles').read_text().splitlines())]

def extend_area13(root,keys,indices,tile,scale,rule,blank):
 conds=['<condition>area13,memoryCheckConstant,004D,==,0D']
 guard='area13&!worldmap&!equipment&!title&!radio'
 backgrounds=[];painted={};mapping={}
 # Match native 8x8 pixels, then sample the geometrically aligned painting.
 for n,asset in [(2040,'area13-exterior.png'),(2520,'area13-interior.png')]:
  native=np.array(Image.open(root/f'capture/area13/{n:05}.png').convert('RGB'))
  src=Image.open(root/'art'/asset).convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
  if n==2040:
   tx=np.interp(np.arange(1024)/4,[0,80,96,112,144,176,192,208,240,256],[0,79,94,111,143,176,192,208,240,256])*4
   ty=np.interp(np.arange(960)/4,[0,48,80,112,128,136,160,176,192,208,240],[0,47,77,108,126,141,157,173,188,204,240])*4
   yy,xx=np.meshgrid(ty,tx,indexing='ij');a=np.array(src)
   src=Image.fromarray(np.stack([map_coordinates(a[:,:,c],[yy,xx],order=1,mode='nearest')for c in range(4)],2).astype('uint8'))
  smooth=np.array(scale(Image.fromarray(native)).convert('RGBA'))
  locations={}
  for y in range(8,233):
   for x in range(249):locations.setdefault(native[y:y+8,x:x+8].tobytes(),(x,y))
  for k,p in sorted({(e[3],e[4])for e in entries(root,n)if e[0]==0}):
   ix=indices(k)
   if len(np.unique(ix))==1:continue
   pos=locations.get(np.array(tile(k,p).convert('RGB')).tobytes())
   if pos is None:continue
   x,y=pos;im=src.crop((x*4,y*4,x*4+32,y*4+32))
   # Preserve actual black apertures and sky pixels at all collision edges.
   a=np.array(im);z=np.repeat(np.repeat(ix==0,4,0),4,1);a[z]=[0,0,0,255]
   if p==0x0F201C0C:
    sky=np.repeat(np.repeat(ix==2,4,0),4,1)
    a[sky]=[0,111,128,255]
   if p==0x0F201C0C:
    # Snow/sky silhouettes are shared among many offset tile combinations.
    # Scale the complete native scene before extracting those cells so the
    # joins remain continuous; use the painting only for material families.
    a=smooth[y*4:y*4+32,x*4:x*4+32].copy()
    sky=np.repeat(np.repeat(ix==2,4,0),4,1);a[sky]=[0,111,128,255]
   painted[k,p]=Image.fromarray(a);mapping[f'{k}:{p:08X}']=[n,x,y,asset]
 rocksource=Image.open(root/'art/area13-exterior.png').convert('RGBA').resize((1024,960))
 for kp,pos in mapping.items():
  k,ph=kp.split(':');p=int(ph,16);n,x,y,_=pos
  if n==2040 and p==0x0F271707 and x in (79,87) and y in (112,120,128,136):
   im=rocksource.crop((316+(x-79)*4,432+(y-112)*4,348+(x-79)*4,464+(y-112)*4))
   a=np.array(im);a[np.repeat(np.repeat(indices(k)==0,4,0),4,1)]=[0,0,0,255]
   painted[k,p]=Image.fromarray(a)
 # A periodic painted-water swatch avoids discontinuities between the eight
 # scrolling/animated foam patterns. Edge values converge to the same teal.
 waterkeys={e[3]for e in entries(root,2040)if e[0]==0 and e[2]>=208 and e[4]==0x0F201C0C}
 water=Image.open(root/'art/area13-exterior.png').convert('RGBA').resize((1024,960)).crop((320,856,352,888))
 wa=np.array(water,dtype=float);yy,xx=np.mgrid[:32,:32]
 w=(np.sin(np.pi*xx/31)*np.sin(np.pi*yy/31))[:,:,None]
 wa[:,:,:3]=np.array([4,83,101])+(wa[:,:,:3]-np.array([4,83,101]))*w*.65
 water=Image.fromarray(np.clip(wa,0,255).astype('uint8'))
 for k in waterkeys:painted[k,0x0F201C0C]=water
 # Uniform wall cells must not inherit a whole scene or repeated decorations.
 exterior=Image.open(root/'art/area13-exterior.png').convert('RGBA').resize((1024,960))
 wall=exterior.crop((720,560,752,592))
 for k,p in keys:
  ix=indices(k);canonical=0x0F000000|(p&0xFFFFFF)
  if canonical in {0x0F200F0C,0x0F20160C,0x0F20230C}:canonical=0x0F201C0C
  im=painted.get((k,canonical))
  if p>>24==255:continue
  if im is None and canonical==0x0F201C0C:
   if np.all(ix==2):im=Image.new('RGBA',(32,32),(0,111,128,255))
   elif np.any(ix==1):
    # Unseen foam/cloud phases use their real shape with smooth edges.
    im=scale(tile(k,canonical))
  if im is None and canonical==0x0F201000 and np.all(ix==2):im=wall
  if im is None:continue
  if canonical==0x0F201C0C:
   a=np.array(im);mask=np.repeat(np.repeat(ix==2,4,0),4,1)
   if p==0x0F201C0C and k not in waterkeys:a[mask]=[0,111,128,255]
   elif k in waterkeys and p!=0x0F201C0C:
    target=np.array(tile('0000000000000000FFFFFFFFFFFFFFFF',p))[0,0,:3]
    a[:,:,:3]=np.clip(a[:,:,:3].astype(float)*.6+target*.4,0,255)
   elif k not in waterkeys:a[mask]=np.array(scale(tile(k,p)))[mask]
   im=Image.fromarray(a)
  if p>>24!=15:
   a=np.array(im);mask=np.repeat(np.repeat(ix==0,4,0),4,1)
   a[mask]=np.array(scale(tile(k,p)))[mask];im=Image.fromarray(a)
  rule(k,p,im,guard)
 # Fully painted guard poses reuse the same native anchor/flip machinery.
 white=[(k,p)for k,p in keys if p==0xFF36300F]
 c,a,v=make_actor(root,white,lambda k,p,im,g=None:rule(k,p,im,(guard+'&'+g)if g is not None else None),blank,'area13',2,0xFF36300F)
 conds+=c;backgrounds+=a
 for actor,pal in [('contact',0xFF202A0F),('neutral',0xFF36150F)]:
  c,a,v=make_actor(root,[(k,p)for k,p in keys if p==pal],lambda k,p,im,g=None:rule(k,p,im,(guard+'&'+g)if g is not None else None),blank,actor,1,pal)
  conds+=c;backgrounds+=a
 # Single-object items and canopy preserve source tile positions and mirrors.
 if (root/'art/area13-items.png').exists():
  sheet=Image.open(root/'art/area13-items.png').convert('RGBA');cw=sheet.width//3
  cells=[]
  for i in range(3):
   im=sheet.crop((i*cw,0,(i+1)*cw,sheet.height));box=im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox();cells.append(im.crop(box))
  for n,box,cell in [(4680,(200,177,216,193),1),(5880,(120,11,136,35),2)]:
   x0,y0,x1,y1=box;im=cells[cell].resize(((x1-x0)*4,(y1-y0)*4),Image.Resampling.LANCZOS)
   for ly,x,y,k,p,h,v in entries(root,n):
    if ly!=1 or not(x0<=x<x1 and y0<=y<y1):continue
    if cell==2 and p!=0xFF36150F:continue
    t=im.crop(((x-x0)*4,(y-y0)*4,(x-x0+8)*4,(y-y0+8)*4))
    if h:t=ImageOps.mirror(t)
    if v:t=ImageOps.flip(t)
    for kk,pp in keys:
     if kk==k and pp>>24==255:rule(k,pp,t,guard)
  # The small green pickup is a background cell, blinking through palette.
  k='';item_candidates=json.loads((root/'capture/area13/item-keys.json').read_text())if(root/'capture/area13/item-keys.json').exists()else[]
  for k,p in item_candidates:rule(k,int(p,16),cells[0].resize((32,32),Image.Resampling.LANCZOS),guard)
 if (root/'art/area13-portraits.png').exists():
  sheet=Image.open(root/'art/area13-portraits.png').convert('RGBA');cw=sheet.width//3;ch=sheet.height//2
  anchor='00030F1F3F7FFFFF00030F1F3F7FFFFF'
  for col,palette in enumerate([0xFF263530,0xFF263515,0xFF263518,0xFF263506]):
   anchor='00010F1F3F7FFFFF00010F1F3F7FFFFF' if col==3 else '00030F1F3F7FFFFF00030F1F3F7FFFFF'
   mouth=['1010080083804060E0E0F0FF7F7FBF9F','0010100F80874060FFE0E0F07F78BF9F','1010080083804060E0E0F0FF7F7FBF9F','300000048160902FC0FFFFF87E1F0FC0'][col]
   talking=sheet.crop((col*cw,ch,(col+1)*cw,2*ch)).resize((192,256),Image.Resampling.LANCZOS)
   # Six-by-eight source tile sprite dimensions, attached to the live helmet.
   art=sheet.crop((col*cw,0,(col+1)*cw,ch)).resize((192,256),Image.Resampling.LANCZOS)
   if col==3:
    informant=Image.open(root/'art/area13-informant.png').convert('RGBA');iw=informant.width//2
    art=informant.crop((0,0,iw,informant.height)).resize((192,256),Image.Resampling.LANCZOS)
    talking=informant.crop((iw,0,2*iw,informant.height)).resize((192,256),Image.Resampling.LANCZOS)
   # Crop into a symmetric 48x64 portrait; the native frame/text stay live.
   for y in range(0,64,8):
    for x in range(-8,40,8):
     vk=hashlib.md5(f'area13portrait:{palette}:{x}:{y}'.encode()).hexdigest().upper()
     backgrounds.append(f'<addition>{anchor},{palette:08X},{x},{y},{vk},{palette:08X},N')
     mouthcond=f'a13mouth{len(conds)}'
     conds.append(f'<condition>{mouthcond},spriteNearby,{8-x},{40-y},{mouth},FF263506,Y')
     rule(vk,palette,talking.crop(((x+8)*4,y*4,(x+16)*4,(y+8)*4)),guard+'&'+mouthcond)
     rule(vk,palette,art.crop(((x+8)*4,y*4,(x+16)*4,(y+8)*4)),guard)
     rule(vk,palette,blank)
   # All native portrait pieces are only hidden near this palette-specific head.
   for dx,dy,k,p,h,v,hp in json.loads((root/'capture/area13/portrait-parts.json').read_text()):
    if hp!=palette:continue
    name=f'a13portrait{len(conds)}';dx=-dx*(-1 if h else 1);dy=-dy*(-1 if v else 1)
    conds.append(f'<condition>{name},spriteNearby,{dx},{dy},{anchor},{palette:08X},N')
    rule(k,p,blank,guard+'&'+name)
 (root/'validation/area13_mapping.json').write_text(json.dumps({'painted':mapping,'guard_pose_count':8,'area_address':'004D','area_value':'0D'},indent=2)+'\n')
 return conds,backgrounds
