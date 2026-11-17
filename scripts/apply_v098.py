"""Repair the Area 5 exhaust: fixed nozzle, complete native-timed flame.

Usage: python scripts/apply_v098.py BASELINE_V097_ZIP CAPTURE_TILES OUTPUT_PACK
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json,sys,zipfile
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
baseline,captures,dest=map(Path,sys.argv[1:4]);dest.mkdir(parents=True,exist_ok=True)
from runtime_baseline import copy_baseline
baseline_sha256=copy_baseline(baseline,dest,'097')
lines=(dest/'hires.txt').read_text().splitlines();image_id=sum(l.startswith('<img>')for l in lines)
HEAD='C7C7C7D7C7C7C7FF4141796979797979'
PHASE=['A8D12F4F9D3D352F5DBEF0F0E2424A50','A8D32E43981C32105DBCF1FCE7634D6F']
GUARD='area5&!title&!worldmap&!equipment&!radio&!areaClear'
pals=set();known=defaultdict(set);existing_add={}
for l in lines:
 if '<tile>'in l:
  a=l.split('<tile>')[1].split(',');known[a[1]].add(int(a[2],16))
 if l.startswith('<addition>'+HEAD+','):
  a=l[10:].split(',');p=int(a[1],16);pals.add(p);existing_add[int(a[2]),int(a[3]),p]=a[4]
native=defaultdict(set)
# Only known exhaust components may be replaced; an overlapping projectile
# must never become part of the nozzle or plume.
components={
 (16,16):{'AA14A952A5499653D5EB57AF5EBE7DBE'},
 (16,24):{'99549251905020E07FB773B170B0E0E0'},
 (24,16):{'AA54A850A0D8FA7456ACD8F07824068C'},
 (24,24):set(PHASE),
 (24,32):{'3A311B2C0E130100454E6413310C1A09','00000000000000006DB9061414040000'},
 (32,24):{'00D0B8FCA8C2B11CC2204200563D4AE3','000000000000000000B080E0F098E000'},
 (32,32):{'CC80C4B038100804107E3A4CC4ECF65A','0000000000000000B080404000000000'},
}
for f in sorted(captures.glob('*.tiles')):
 es=[s.split(',')for s in f.read_text().splitlines()];h=next((e for e in es if e[0]=='1'and e[3]==HEAD),None)
 if h:
  hx,hy=map(int,h[1:3])
  for l,x,y,k,p,h,v in es:
   dx,dy=int(x)-hx,int(y)-hy
   if l=='1'and k in components.get((dx,dy),set()):native[dx,dy].add(k)
assert dict(native)==components,'Capture is missing one or more exhaust states'

# Separate generated hardware and flame layers. The identical hardware layer
# is reused in both phases; only the orange exhaust changes shape.
src=Image.open(ROOT/'art/area5-exhaust-v098.png').convert('RGBA');cw=src.width//3
hardware=Image.new('RGBA',(cw,cw));hardware.paste(src.crop((0,0,650,560)),(0,0))
hardware=hardware.resize((96,96),Image.Resampling.LANCZOS)
hardware_canvas=Image.new('RGBA',(128,128));hardware_canvas.alpha_composite(hardware,(0,0))
flames=[]
for col,size in [(2,(58,58)),(1,(50,50))]:
 flame=src.crop((cw*col+330,380,cw*col+710,710))
 # Retain the full generated alpha contour and a transparent margin.
 box=flame.getchannel('A').getbbox();assert box
 flame=flame.crop(box).resize(size,Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(128,128));canvas.alpha_composite(flame,(66,50));flames.append(canvas)
 assert canvas.getchannel('A').getbbox()[2]<128 and canvas.getchannel('A').getbbox()[3]<128
atlas=Image.new('RGBA',(1024,1024));cache={};conds=[];cc={};rules=[];additions=[]
for dx in [16,24,32,40]:conds.append(f'<condition>exhaust098_wrapped{dx},originPositionCheckX,<,{dx}')
def condition(dx,dy,k,p=0xFF30150F,ignore=True):
 key=(dx,dy,k,p,ignore)
 if key not in cc:
  name=f'exhaust098_{len(cc)}';cc[key]=name;conds.append(f'<condition>{name},spriteNearby,{dx},{dy},{k},{p:08X},{"Y"if ignore else"N"}')
 return cc[key]
def emit(k,p,im,guard=None):
 b=im.tobytes()
 if b not in cache:
  i=len(cache);x,y=i%32*32,i//32*32;atlas.paste(im,(x,y));cache[b]=(x,y)
 x,y=cache[b];rules.append((f'[{guard}]'if guard else'')+f'<tile>{image_id},{k},{p:08X},{x},{y},1,N')
blank=Image.new('RGBA',(32,32))
canvases={}
for hp in sorted(pals):
 ar=np.array(hardware_canvas)
 if hp!=0xFF30150F:ar[:,:,:3]=np.clip(ar[:,:,:3].astype(float)*1.1,0,255).astype('uint8')
 for phase in [0,1]:
  im=Image.fromarray(ar);im.alpha_composite(flames[phase]);canvases[hp,phase]=im
for dy in range(16,48,8):
 for dx in range(16,48,8):
  box=((dx-16)*4,(dy-16)*4,(dx-8)*4,(dy-8)*4)
  present=any(c.crop(box).getchannel('A').getbbox()for c in canvases.values())
  # Existing native or virtual cells are also overwritten with transparency
  # where necessary, so no fragment of the former animated claw survives.
  if not present and (dx,dy)not in native and not any((dx,dy,p)in existing_add for p in pals):continue
  if (dx,dy)in native:
   for k in sorted(native[dx,dy]):
    for p in sorted(known[k]):
     if p>>24!=0xFF:continue
     for hp in sorted(pals):
      head_guard=GUARD+'&'+condition(-dx,-dy,HEAD,hp,False)
      # The game clamps a wrapped native sprite to x=0, which can leave its
      # offset one to seven pixels short of the moving head. Cover that
      # interval so the first column cannot leak the older flame graphic.
      for shift in [0,7]:
       wrapped_guard=GUARD+'&'+condition(256-dx+shift,-dy,HEAD,hp,False)+f'&exhaust098_wrapped{dx}'
       emit(k,p,blank,wrapped_guard)
      for phase in [0,1]:emit(k,p,canvases[hp,phase].crop(box),head_guard+'&'+condition(24-dx,24-dy,PHASE[phase]))
      fallback=0 if k not in [PHASE[1],'00000000000000006DB9061414040000','000000000000000000B080E0F098E000','0000000000000000B080404000000000']else 1
      emit(k,p,canvases[hp,fallback].crop(box),head_guard)
  else:
   for hp in sorted(pals):
    vk=existing_add.get((dx,dy,hp))
    if vk is None:
     vk=hashlib.md5(f'exhaust098:{dx}:{dy}'.encode()).hexdigest().upper()
     additions.append(f'<addition>{HEAD},{hp:08X},{dx},{dy},{vk},{hp:08X},N')
    for phase in [0,1]:emit(vk,hp,canvases[hp,phase].crop(box),GUARD+'&'+condition(24-dx,24-dy,PHASE[phase]))
    emit(vk,hp,canvases[hp,0].crop(box),GUARD);emit(vk,hp,blank)
lines[0]='# Bionic Commando HD v0.9.8 - Fixed rear nozzle and complete animated exhaust'
i=next(i for i,l in enumerate(lines)if '<tile>'in l);lines[i:i]=['<img>area5-exhaust-v098.png']+conds+additions+rules
(dest/'hires.txt').write_text('\n'.join(lines)+'\n');atlas.crop((0,0,1024,((len(cache)+31)//32)*32)).save(dest/'area5-exhaust-v098.png')
readme=(dest/'README.txt').read_text().replace('v0.9.7','v0.9.8')
readme=readme.replace('Area 5 doorway facade, boss overlap and generator hit feedback','Area 5 fixed rear nozzle and complete animated exhaust')
readme=readme.replace('cannon and two native-timed claw states.','cannon, fixed exhaust nozzle and two native-timed flame states.')
readme+='\nV0.9.8: Fixed Area 5 rear thruster housing, restored the full exhaust plume and kept its original animation timing.\n';(dest/'README.txt').write_text(readme)
(ROOT/'validation').mkdir(exist_ok=True)
report={'version':'0.9.8','baseline_sha256':baseline_sha256,'native_component_positions':{f'{x},{y}':sorted(k)for(x,y),k in native.items()},'new_additions':len(additions),'new_rules':len(rules),'hardware_shared_between_phases':True,'flame_phases':2,'patch_native_bounds':[16,16,48,48],'conditions':len(conds)}
(ROOT/'validation/v098-build.json').write_text(json.dumps(report,indent=2)+'\n')
for p in [0,1]:canvases[0xFF30150F,p].save(ROOT/f'validation/v098-composite-{p}.png')
print(json.dumps({k:v for k,v in report.items()if k!='native_component_positions'},indent=2))
