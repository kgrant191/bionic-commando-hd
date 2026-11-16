"""Package the v0.8.1 runtime and an actual-emulator review contact sheet."""
from pathlib import Path
import argparse,zipfile,json,hashlib
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--replays',type=Path,required=True);p.add_argument('--mode',default='review');p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
r=Path(__file__).resolve().parents[1];font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
scenes=[('coldboot',60,'BOOT / POWER CYCLE'),('intro',2280,'STORY / HEADQUARTERS'),('intro',3360,'STORY / SUPER JOE'),('5',1560,'SOLID EARTH / FACTORY'),('5',2280,'BARRELS / PLATFORMS'),('5',6840,'HELICOPTER INFANTRY / MACHINERY'),('5',10800,'CONSISTENT KNIFE GUARD'),('5',17400,'VISIBLE COIL SPRINGS'),('5',20880,'FLOATING ROBOT BOSS'),('cave',3600,'CAVE GOAL DOORFRAME'),('15',1080,'OVERHEAD COMBAT'),('15',1440,'BUNKER / BARRICADES'),('15',2880,'TALKING PORTRAITS'),('15',4320,'RED-HAIRED 1UP / ROOM'),('15',6000,'COLORED RADIO / BARRIER')]
w,h=512,478;canvas=Image.new('RGB',(3*w+48,110+5*h+36),(13,19,26));d=ImageDraw.Draw(canvas)
d.text((24,18),'BIONIC COMMANDO HD — v0.8.1',font=ImageFont.truetype(font,30),fill=(241,210,131));d.text((24,62),'Actual MesenCE replay screenshots · Review build',font=ImageFont.truetype(font,20),fill=(180,197,204))
for i,(movie,n,title)in enumerate(scenes):
 x=24+i%3*w;y=110+i//3*h
 d.text((x,y),title,font=ImageFont.truetype(font,16),fill=(220,228,232))
 im=Image.open(a.replays/movie/a.mode/'frames'/f'{n:05}.png').convert('RGB').resize((496,434),Image.Resampling.LANCZOS)
 canvas.paste(im,(x,y+28))
preview=a.output/'Bionic_Commando_HD_v0.8.1_Preview.png';canvas.save(preview)
allowed={'hires.txt','README.txt'}
for line in(r/'pack/hires.txt').read_text().splitlines():
 body=line.split(']',1)[-1]if line.startswith('[')else line
 if body.startswith('<img>'):allowed.add(body[5:])
 if body.startswith('<background>'):allowed.add(body[12:].split(',')[0])
assert {p.name for p in(r/'pack').iterdir()if p.is_file()}==allowed,'Unused or missing runtime file'
install=a.output/'Bionic_Commando_HD_v0.8.1.zip'
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for name in sorted(allowed):z.write(r/'pack'/name,name)
with zipfile.ZipFile(install)as z:assert z.testzip()is None
print(json.dumps([{'filename':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in[install,preview]],indent=2))
