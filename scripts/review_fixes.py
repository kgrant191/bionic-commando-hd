"""Native-state corrections from the v0.8.0 review; no gameplay writes."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from poses import make_actor
from level_polish import fade_aliases

def entries(root,movie,n):
 return [(int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6]))for a in(l.split(',')for l in(root/f'capture/review-v081/{movie}-{n:05}.tiles').read_text().splitlines())]

def fit(im,size):
 im=im.convert('RGBA');b=im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
 return im.crop(b).resize(size,Image.Resampling.LANCZOS)

def extend_review(root,keys,indices,tile,scale,rule,blank):
 conds=['<condition>bootTitle,memoryCheckConstant,00CE,==,00',
        '<condition>area1,memoryCheckConstant,004D,==,01',
        '<condition>townRoom,memoryCheckConstant,004C,==,38,F8',
        '<condition>knifeAreas,memoryCheckConstant,004D,==,04,FE',
        '<condition>portraitLeft,positionCheckX,>=,168',
        '<condition>portraitRight,positionCheckX,<,224',
        '<condition>portraitTop,positionCheckY,>=,48',
        '<condition>portraitBottom,positionCheckY,<,136']
 bg=['[introMode&introArea&bootTitle]<background>title.png,1,0,0,30']
 normal='!title&!worldmap&!equipment&!radio&!areaClear'
 materials=Image.open(root/'art/area5-materials-v081.png').convert('RGBA').resize((1536,1024))
 dirt=materials.crop((24,24,488,488)).resize((64,64),Image.Resampling.LANCZOS)
 # A full repeatable earth material replaces the entire lava-pattern family.
 ground={(k,p)for ly,x,y,k,p,h,v in entries(root,'5',1560)if ly==0 and y>=208 and p==0x0F372616}
 earth={}
 for k,p in ground:
  # Shared rock variants receive stable, non-glowing texture quadrants.
  seed=int(k[:8],16);x=(seed%2)*32;y=(seed//2%2)*32
  earth[k,p]=dirt.crop((x,y,x+32,y+32))
 # Background panels are rebuilt by material bands, not unrelated screenshot crops.
 olive=materials.crop((610,110,710,410)).resize((32,32),Image.Resampling.LANCZOS)
 red=materials.crop((1130,110,1430,410)).resize((32,32),Image.Resampling.LANCZOS)
 panel={}
 for k,p in keys:
  if p==0x0F261606 and len(np.unique(indices(k)))==1 and np.any(indices(k)):
   panel[k,p]=blank
 # A continuous distant wall avoids the repeated 8-pixel red checkerboard.
 materials.crop((1100,610-512,1480,920-512)).resize((1024,960),Image.Resampling.LANCZOS).save(root/'pack/area5-distant-wall.png')
 bg.append('[area5&'+normal+']<background>area5-distant-wall.png,1,0,0,1')
 # Exact barrel cell dimensions; no padded miniature inside the native cell.
 barrel=materials.crop((76,522,435,1007)).resize((32,64),Image.Resampling.LANCZOS)
 for ly,x,y,k,p,h,v in entries(root,'5',2280):
  if ly==0 and x==90 and 147<=y<163:panel[k,p]=barrel.crop((0,(y-147)*4,32,(y-139)*4))
 # Two visible helical coils beneath a thin bounce plate.
 spring=materials.crop((516,644,1017,1004)).resize((128,64),Image.Resampling.LANCZOS)
 for ly,x,y,k,p,h,v in entries(root,'5',17400):
  if ly==0 and 152<=x<184 and 15<=y<31:panel[k,p]=spring.crop(((x-152)*4,(y-15)*4,(x-144)*4,(y-7)*4))
 door=materials.crop((1028,516,1532,1020)).resize((128,128),Image.Resampling.LANCZOS)
 # A modular header and jamb keeps the aperture open and joins at tile boundaries.
 door.paste((0,0,0,255),(24,32,104,128))
 def frame(es,box,guard):
  x0,y0,x1,y1=box;art=door.resize(((x1-x0)*4,(y1-y0)*4),Image.Resampling.LANCZOS)
  for ly,x,y,k,p,h,v in es:
   if ly!=0 or k=='0'*32 or not(x0<=x<x1 and y0<=y<y1):continue
   im=art.crop(((x-x0)*4,(y-y0)*4,(x-x0+8)*4,(y-y0+8)*4))
   for kk,pp in keys:
    if kk==k and pp>>24!=255:rule(k,pp,im,guard)
 frame(entries(root,'5',11640),(198,130,230,162),'area5&'+normal)
 frame(entries(root,'5',10800),(32,160,64,192),'area5&'+normal)
 frame(entries(root,'15',4320),(32,160,64,192),'area15&townRoom&'+normal)
 cave=[(int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6]))for a in(l.split(',')for l in(root/'capture/feedback-v050/00060.tiles').read_text().splitlines())]
 frame(cave,(92,64,124,96),'area1&'+normal)
 # Boss-room shutters use horizontal slats, with the native two-column width.
 shutter=Image.new('RGBA',(64,128),(32,43,48,255));d=ImageDraw.Draw(shutter)
 for y in range(0,128,32):
  d.rectangle((6,y,57,y+28),fill=(65,80,84),outline=(125,145,147),width=2)
  d.line((9,y+5,54,y+5),fill=(158,176,175),width=2)
  d.line((8,y+25,55,y+25),fill=(11,23,29),width=3)
 d.rectangle((0,0,5,127),fill=(126,98,62));d.rectangle((58,0,63,127),fill=(126,98,62))
 for a in(l.split(',')for l in(root/'capture/feedback-v050/03660.tiles').read_text().splitlines()):
  ly,x,y,k,p=int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4])
  if ly==0 and 64<=x<80 and 160<=y<192 and k!='0'*32:rule(k,p,shutter.crop(((x-64)*4,(y-160)*4,(x-56)*4,(y-152)*4)),'area1&'+normal)
 for paint in [earth,panel]:
  aliases=fade_aliases(paint)
  for k,p in keys:
   im=paint.get((k,p))
   if im is None and(k,p)in aliases:
    base,f=aliases[k,p];a=np.array(paint[k,base]);a[:,:,:3]=(a[:,:,:3]*f).astype('uint8');im=Image.fromarray(a)
   if im is not None:rule(k,p,im,'area5&'+normal)
 # New nonhuman compact machine keeps the original mirrored quarter layout.
 machine=fit(Image.open(root/'art/ceiling-machine-v081.png'),(64,64))
 for k,x,y in [('FFFFFEF8FCCC5ECC2445FE18244CD2CC',32,0),('1F0FBFBF05FC0300140C4440FEFF0300',0,32)]:
  for kk,p in keys:
   if kk==k and p>>24==255:rule(k,p,machine.crop((x,y,x+32,y+32)),'area5&'+normal)
 # Full robot and genuine overhead poses; source art selected from native aim.
 for actor,pal,guard in [('area5boss',0xFF30210F,'area5&'+normal),('overhead-green',0xFF202A0F,'interception&'+normal),('overhead-red',0xFF36150F,'interception&'+normal)]:
  selected=keys
  c,a,_=make_actor(root,selected,lambda k,p,im,g=None:rule(k,p,im,guard+'&'+g if g else None),blank,actor,2,pal)
  conds+=c;bg+=a
 # Radio variations use the same complete four-quarter painting. Keep the
 # native colored case readable, including the new pink menu/yellow pickup.
 source=Image.open(root/'art/equipment-lamp-v4.png').convert('RGBA');cw=source.width//3
 radio=fit(source.crop((cw,0,cw*2,source.height)),(64,64))
 radio_parts=[e for e in entries(root,'15',5760)if e[0]==1 and 200<=e[1]<216 and 49<=e[2]<65]
 radio_parts += [(int(a[0]),int(a[1])-128+200,int(a[2])-193+49,a[3],int(a[4]),int(a[5]),int(a[6])) for a in(l.split(',')for l in(root/'capture/ui/equipment.tiles').read_text().splitlines())if a[0]=='1'and 128<=int(a[1])<144 and 193<=int(a[2])<209]
 for ly,x,y,k,p,h,v in radio_parts:
  for kk,pp in keys:
   if kk!=k or pp>>24!=255:continue
   im=radio.crop(((x-200)*4,(y-49)*4,(x-192)*4,(y-41)*4));a=np.array(im)
   # Shade case by the native dominant chromatic ink, retaining highlights.
   colors=np.array(tile('0000000000000000FFFFFFFFFFFFFFFF',pp))[0,0,:3].astype(float)
   if colors.max()>40:
    ratio=colors/max(colors.max(),1);gray=a[:,:,:3].mean(2);mask=(a[:,:,3]>0)&(gray<180)
    a[mask,:3]=np.clip(gray[mask,None]*(.4+.8*ratio),0,255).astype('uint8')
   if h:im=ImageOps.mirror(Image.fromarray(a))
   else:im=Image.fromarray(a)
   rule(k,pp,im,'!title&!radio')
 # 1UP has two mirrored native halves: retain red hair through both palettes.
 life=fit(Image.open(root/'art/spencer-life-v081.png'),(64,64))
 for k,y in [('1420202417170F3F1D3F3F3B1A1A0C37',0),('489C9FF8711E3EFC77FBFF9F7F1E3EFC',32)]:
  for kk,p in keys:
   if kk==k and p>>24==255:rule(k,p,life.crop((0,y,32,y+32)),'!title&!interception')
 # Native dialogue mouth pieces use further patterns in Area 15. Hide all
 # observed portrait-colored pieces inside the portrait box, including blink
 # frames, while additions supply the approved talking portrait.
 for k,p in keys:
  if p>>8 in {0xFF2635,0xFF2636} or p==0xFF303526:rule(k,p,blank,'area13&portraitLeft&portraitRight&portraitTop&portraitBottom')
 # Metal barricade geometry is code-native and cut by the original tile grid.
 terrain=Image.open(root/'art/interception-terrain-v081.png').convert('RGBA').resize((1024,960))
 barrier=terrain.crop((384,224,640,288)).resize((128,64),Image.Resampling.LANCZOS)
 for ly,x,y,k,p,h,v in entries(root,'15',1080):
  if ly==0 and 96<=x<160 and 56<=y<72 and p==0x0F201000:
   rule(k,p,barrier.crop((((x-96)%32)*4,(y-56)*4,((x-96)%32)*4+32,(y-48)*4)),'interception&'+normal)
 # The orange room barrier is an OAM object, distinct from the supply chest.
 room_barrier=Image.new('RGBA',(128,64),(44,56,62,255));bd=ImageDraw.Draw(room_barrier)
 bd.rectangle((3,3,124,60),fill=(78,93,96),outline=(180,162,107),width=5)
 bd.rectangle((14,13,113,49),fill=(31,43,50),outline=(119,137,137),width=3)
 for x in [5,116]:
  bd.rectangle((x,1,x+7,62),fill=(174,132,51));bd.ellipse((x+1,8,x+5,12),fill=(222,224,191));bd.ellipse((x+1,50,x+5,54),fill=(222,224,191))
 seen=set()
 for ly,x,y,k,p,h,v in entries(root,'15',4320):
  if ly!=1 or not(138<=x<170 and 145<=y<161) or k in seen:continue
  seen.add(k);im=room_barrier.crop(((x-138)*4,(y-145)*4,(x-130)*4,(y-137)*4))
  if h:im=ImageOps.mirror(im)
  for kk,pp in keys:
   if kk==k and pp>>24==255:rule(k,pp,im,'area15&townRoom&'+normal)
 # A separate three-pattern gunner sits behind barricades; it has no walking
 # torso anchor. Replace his visible helmet, shoulders and rifle directly.
 sh=Image.open(root/'art/overhead-commandos-v081.png').convert('RGBA');cw,ch=sh.width//4,sh.height//2
 gunner=fit(sh.crop((0,ch,cw,ch*2)),(64,112)).crop((0,0,64,64))
 seen=set()
 for ly,x,y,k,p,h,v in entries(root,'15',1080):
  if ly!=1 or not(72<=x<88 and 203<=y<219) or k=='0'*32 or k in seen:continue
  seen.add(k);im=gunner.crop(((x-72)*4,(y-203)*4,(x-64)*4,(y-195)*4))
  if h:im=ImageOps.mirror(im)
  rule(k,p,im,'interception&'+normal)
 # Native red-hair overlays otherwise sit on top of the painted Spencer head.
 for k,p in keys:
  if p==0xFF36060F:rule(k,p,blank,'interception&'+normal)
  if k in {'00000000182424180000000000181800','00000000183C3C1800000000183C3C18'} and p>>24==255:
   a=np.zeros((8,8,4),dtype='uint8');a[indices(k)>0]=[246,210,121,255]
   rule(k,p,scale(Image.fromarray(a)),'interception&'+normal)
 # Boss impact fragments use the existing painted explosion family.
 fx=Image.open(root/'art/effects-v5.png').convert('RGBA');fx=fit(fx.crop((0,0,round(fx.width*510/2208),fx.height)),(64,64))
 for k,y in [('00D0B8FCA8C2B11CC2204200563D4AE3',0),('CC80C4B038100804107E3A4CC4ECF65A',32)]:
  for kk,p in keys:
   if kk==k and p>>24==255:rule(k,p,fx.crop((32,y,64,y+32)),'area5&'+normal)
 # Finish the overhead exit building from its own native reference.
 bunker=Image.open(root/'art/interception-bunker-v081.png').convert('RGBA').resize((256,224),Image.Resampling.LANCZOS)
 for ly,x,y,k,p,h,v in entries(root,'15',1440):
  if ly==0 and 96<=x<160 and -7<=y<49 and p==0x0F201000 and k!='0'*32:
   dy=max(0,(y-1)*4);im=bunker.crop(((x-96)*4,dy,(x-88)*4,dy+32))
   rule(k,p,im,'interception&'+normal)
 # This cave goal uses a wing-emblem header, unlike the radio's arrows.
 for x,y,k,p in json.loads((root/'capture/review-v081/cave-goal-frame.json').read_text()):
  rule(k,p,door.crop((x*4,y*4,x*4+32,y*4+32)),'area1&'+normal)
 # The second weapon's four native components also appear in the menu slot.
 weapon=fit(Image.open(root/'art/heavy-weapon-icon-v081.png'),(64,64))
 for ly,x,y,k,p,h,v in entries(root,'15',2160):
  if ly==1 and 32<=x<48 and 193<=y<209:
   for kk,pp in keys:
    if kk==k and pp>>24==255:rule(k,pp,weapon.crop(((x-32)*4,(y-193)*4,(x-24)*4,(y-185)*4)),'equipment')
 # All expanding/contracting impact phases at the robot's right edge.
 for k,dx,dy in json.loads((root/'capture/review-v081/boss-impact-parts.json').read_text()):
  for kk,p in keys:
   if kk==k and p>>24==255:
    sy=0 if dy<=24 else 32
    rule(k,p,fx.crop((32,sy,64,sy+32)),'area5&'+normal)
 # Tall cover blocks use a second eight-pattern family at encounter start.
 tall=barrier.resize((128,128),Image.Resampling.LANCZOS)
 for ly,x,y,k,p,h,v in entries(root,'15',720):
  if ly==0 and p==0x0F201000 and 128<=x<160 and 128<=y<160:
   rule(k,p,tall.crop(((x-128)*4,(y-128)*4,(x-120)*4,(y-120)*4)),'interception&'+normal)
 # Plain road variants share one edge-continuous painted dirt material. This
 # prevents unrelated screenshot gradients from making an 8px checkerboard.
 roadkeys={k for ly,x,y,k,p,h,v in entries(root,'15',1080)if ly==0 and 104<=x<168 and p==0x0F271707 and k!='0'*32}
 sw=np.array(terrain.crop((420,600,452,632))).astype(float);yy,xx=np.mgrid[:32,:32]
 weight=(np.sin(np.pi*xx/31)*np.sin(np.pi*yy/31))[:,:,None]
 mean=sw[:,:,:3].mean((0,1));sw[:,:,:3]=mean+(sw[:,:,:3]-mean)*weight*.65
 earthroad=Image.fromarray(np.uint8(np.clip(sw,0,255)))
 for k in roadkeys:rule(k,0x0F271707,earthroad,'interception&'+normal)
 # Area 15 uses shield insignia where Area 13 used a medical sign. Rebuild
 # the plaque as native vector geometry rather than scaling its white pixels.
 plaque=Image.new('RGBA',(192,96));pd=ImageDraw.Draw(plaque)
 for y in range(96):
  tone=round(83-25*y/95);pd.line((0,y,191,y),fill=(tone,tone+9,tone+10,255))
 pd.rectangle((1,1,190,94),outline=(190,177,143),width=3)
 pd.line((5,5,186,5),fill=(218,219,197),width=2)
 pd.line((5,90,186,90),fill=(22,29,30),width=3)
 for x in (10,181):
  for y in (12,83):pd.ellipse((x-3,y-3,x+3,y+3),fill=(175,182,173),outline=(28,34,32),width=1)
 for side in (-1,1):
  for y in (30,42,54):
   pd.line((96+side*40,y,96+side*70,y),fill=(169,149,104),width=3)
 pd.polygon([(68,16),(123,16),(120,54),(113,67),(96,80),(79,67),(71,54)],fill=(181,156,101))
 pd.polygon([(74,22),(117,22),(114,53),(108,62),(96,72),(84,62),(77,53)],fill=(35,49,52))
 pd.line((96,26,96,61),fill=(214,195,143),width=5)
 pd.line((88,34,104,34),fill=(214,195,143),width=4)
 for base_y in (94,174):
  for ly,x,y,k,p,h,v in entries(root,'15',5400):
   if ly==0 and p==0x0F201000 and 70<=x<118 and base_y<=y<base_y+24:
    name=f'townShield{x}_{y}'
    conds.append(f'<condition>{name},tileNearby,{86-x},{base_y-y},81FFE0E9E9E9E9E96E001F1616161616,0F201000,N')
    rule(k,p,plaque.crop(((x-70)*4,(y-base_y)*4,(x-62)*4,(y-base_y+8)*4)),'area15&!townRoom&'+normal+'&'+name)
 return conds,bg
