"""Area 4 materials and guards. Native palette states retain darkness/fades."""
import json
import numpy as np
from PIL import Image,ImageOps
from poses import make_actor
from items import pickup_art
from level_polish import fade_aliases

def extend_area4(root,keys,indices,tile,scale,rule,blank):
 guard='!interception&area4&!title&!worldmap&!equipment&!radio&!areaClear'
 conditions=['<condition>area4,memoryCheckConstant,004D,==,04'];additions=[]
 painted={};mapping={}
 exterior=Image.open(root/'art/area4-exterior.png').convert('RGBA').resize((1024,960))
 exterior.crop((200,0,568,768)).resize((1024,960),Image.Resampling.LANCZOS).save(root/'pack/area4-distance.png')
 additions.append(f'[{guard}&screenEnabled]<background>area4-distance.png,1,0,0,1')
 forest={a[3]for a in (l.split(',')for l in (root/'capture/area4/00600.tiles').read_text().splitlines())if a[0]=='0'and int(a[4])==0x0F19090B and 48<=int(a[1])<144}
 for k,p in keys:
  if p==0x0F311C01:
   # Palette zero is also used for the black voids between cave spikes.
   a=np.zeros((32,32,4),dtype='uint8');a[:,:,3]=0 if np.any(indices(k)) else 255
   rule(k,p,Image.fromarray(a),guard)
  elif p==0x0F19090B and k in forest and np.any(indices(k)):rule(k,p,blank,guard)
 # Keep inventory additions independent of gameplay tile families.
 sheet=Image.open(root/'art/area4-items.png').convert('RGBA');cw=sheet.width//2
 for n,x0,y0,col in [(240,48,73,0),(360,48,73,1)]:
  cell=sheet.crop((col*cw,0,(col+1)*cw,sheet.height))
  if col==0:cell=pickup_art(root)[1]
  else:cell=cell.crop(cell.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()).resize((64,64),Image.Resampling.LANCZOS)
  for a in (l.split(',')for l in (root/f'capture/area4/{n:05}.tiles').read_text().splitlines()):
   ly,x,y,k,p,h,v=int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6])
   if ly!=1 or not(x0<=x<x0+16 and y0<=y<y0+16):continue
   t=cell.crop(((x-x0)*4,(y-y0)*4,(x-x0+8)*4,(y-y0+8)*4))
   if h:t=ImageOps.mirror(t)
   if v:t=ImageOps.flip(t)
   rule(k,p,t,'equipment');rule(k,p,t,'worldmap')
 rock=Image.open(root/'art/area4-cave.png').convert('RGBA').resize((1024,960)).crop((64,64,128,128))
 # Tile-periodic rock material avoids disconnected crops from different walls.

 for n,name in [(600,'area4-exterior.png'),(1320,'area4-cave.png'),(1560,'area4-pipes.png'),(6000,'area4-shaft.png')]:
  native=np.array(Image.open(root/f'capture/area4/{n:05}.png').convert('RGB'))
  art=Image.open(root/'art'/name).convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
  loc={}
  for y in range(8,233):
   for x in range(249):loc.setdefault(native[y:y+8,x:x+8].tobytes(),(x,y))
  es=[l.split(',')for l in (root/f'capture/area4/{n:05}.tiles').read_text().splitlines()]
  for k,p in sorted({(a[3],int(a[4]))for a in es if a[0]=='0'}):
   ix=indices(k)
   if len(np.unique(ix))<2 or (k,p)in painted:continue
   pos=loc.get(np.array(tile(k,p).convert('RGB')).tobytes())
   if pos is None:continue
   x,y=pos;im=art.crop((x*4,y*4,x*4+32,y*4+32));a=np.array(im)
   # Preserve native black apertures so art cannot close holes or spike gaps.
   stone=p==0x0F201000 and (n==600 or (n==1320 and (y<96 or y>=208 or (120<=x<144 and 160<=y<208))) or (n==1560 and (y<16 or x>=232 or (y>=128 and x<104) or (y>=164 and x<232))) or (n==6000 and x>=168))
   if stone:
    rx=(x//8%2)*32;ry=(y//8%2)*32
    im=rock.crop((rx,ry,rx+32,ry+32));a=np.array(im)
    if (ix==0).sum()>20:
     mask=np.array(scale(Image.fromarray(np.uint8(ix>0)*255)).convert('RGB'))[:,:,0]/255
     a[:,:,:3]=(a[:,:,:3]*mask[:,:,None]).astype('uint8')
   else:
    # Painted mesh already contains its holes; a second native mask creates
    # jagged disconnected wires when the detailed grid has different spacing.
    pass
   assert np.all(a[:,:,3]==255),(n,k,p,'Unexpected background transparency')
   painted[k,p]=Image.fromarray(a);mapping[f'{k}:{p:08X}']=[n,x,y,name]
 # Open goal doorway: a painted wing-emblem header and copper jambs.
 # Keep its aperture black and exclude the shared all-zero pattern.
 native=np.array(Image.open(root/'capture/area4/09240.png').convert('RGB'))
 door=Image.new('RGBA',(128,128),(0,0,0,255))
 emblem=Image.open(root/'art/closed-door-v4.2.png').convert('RGBA')
 emblem=emblem.crop((0,round(emblem.height*.45),emblem.width,round(emblem.height*.67)))
 door.paste(emblem.resize((128,32),Image.Resampling.LANCZOS),(0,0))
 copper=Image.open(root/'art/area4-cave.png').convert('RGBA').resize((1024,960)).crop((104,424,128,520)).resize((16,96),Image.Resampling.LANCZOS)
 door.paste(copper,(0,32));door.paste(copper,(112,32))
 loc={native[y:y+8,x:x+8].tobytes():(x,y)for y in range(75,100)for x in range(201,226)}
 for k,p in keys:
  if p!=0x0F271606 or not np.any(indices(k)):continue
  xy=loc.get(np.array(tile(k,p).convert('RGB')).tobytes())
  if xy is None:continue
  x,y=xy
  painted[k,p]=door.crop(((x-201)*4,(y-75)*4,(x-193)*4,(y-67)*4))
  mapping[f'{k}:{p:08X}']=[9240,x,y,'goal-door-from-existing-painted-assets']
 # Radio-door header is a different native pattern from the goal insignia.
 radio_emblem=Image.open(root/'art/closed-door-v4.2.png').convert('RGBA')
 radio_emblem=radio_emblem.crop((0,round(radio_emblem.height*.32),radio_emblem.width,round(radio_emblem.height*.67)))
 door.paste(radio_emblem.resize((128,32),Image.Resampling.LANCZOS),(0,0))
 for a in (l.split(',')for l in (root/'capture/area4/01920.tiles').read_text().splitlines()):
  ly,x,y,k,p=int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4])
  if ly!=0 or p!=0x0F271606 or not(140<=x<172 and 126<=y<158)or not np.any(indices(k)):continue
  painted[k,p]=door.crop(((x-140)*4,(y-126)*4,(x-132)*4,(y-118)*4))
  mapping[f'{k}:{p:08X}']=[1920,x,y,'radio-door-from-existing-painted-assets']
 fades=fade_aliases(painted)
 for k,p in keys:
  if p>>24==255:continue
  im=painted.get((k,p))
  if im is None and (k,p)in fades:
   base,factor=fades[k,p];a=np.array(painted[k,base]);a[:,:,:3]=(a[:,:,:3]*factor).astype('uint8');im=Image.fromarray(a)
  # The unlit cave uses black/cyan palettes, not a normal art fade. Keep its
  # original visibility: never show the full painting through the darkness.
  if im is not None:rule(k,p,im,guard)
 # The Area 4 boss has a separate netted-helmet portrait and two mouths.
 conditions += ['<condition>area4BossFace,spriteAtPosition,183,57,00030F1A3D6AF5DA00030F1A3D6AF5DA,FF263515,N',
                '<condition>area4BossTalk,spriteAtPosition,191,97,FFFEC080A0F01FC4FFFFE0400000E038,FF263506,N']
 faces=Image.open(root/'art/area4-boss-portrait.png').convert('RGBA');fw=faces.width//2
 for i in range(2):
  overlay=Image.new('RGBA',(1024,960));face=faces.crop((i*fw,0,(i+1)*fw,faces.height)).resize((192,256),Image.Resampling.LANCZOS)
  overlay.paste(face,(700,228));overlay.save(root/f'pack/area4-boss{i}.png')
  talk='area4BossTalk' if i else '!area4BossTalk'
  additions.append(f'[{guard}&area4BossFace&{talk}]<background>area4-boss{i}.png,1,0,0,20')
 portrait_parts={ (k,p)for state in json.loads((root/'capture/area4/boss-portrait-states.json').read_text()) for x,y,k,p,h,v in state['parts']}
 for k,p in portrait_parts:rule(k,p,blank,guard+'&area4BossFace')
 c,a,v=make_actor(root,keys,lambda k,p,im,g=None:rule(k,p,im,(guard.replace('area4','knifeAreas')+'&'+g)if g else None),blank,'area4',1,0xFF36150F)
 conditions+=c;additions+=a
 (root/'validation/area4_mapping.json').write_text(json.dumps({'painted':mapping,'actor_records':6,'area_address':'004D','area_value':'04'},indent=2)+'\n')
 return conditions,additions
