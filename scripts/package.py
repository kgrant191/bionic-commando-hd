"""Package runtime files and matching emulator screenshots for v0.8.0 review."""
from pathlib import Path
import argparse,zipfile,json,hashlib
from PIL import Image,ImageDraw,ImageFont
parser=argparse.ArgumentParser()
parser.add_argument('--replays',type=Path,required=True)
parser.add_argument('--mode',default='verified')
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
r=Path(__file__).resolve().parents[1];font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
scenes=[('intro',2280,'STORY — HEADQUARTERS'),('intro',3360,'STORY — SUPER JOE'),('5',2280,'AREA 5 — FACTORY'),('5',6840,'AREA 5 — SHAFT / BLUE GUARDS'),('15',1080,'OVERHEAD INTERCEPTION'),('15',4920,'AREA 15 — SUPPLY ROOM')]
canvas=Image.new('RGB',(1072,140+len(scenes)*500),(13,19,26));d=ImageDraw.Draw(canvas)
d.text((24,18),'BIONIC COMMANDO HD — v0.8.0',font=ImageFont.truetype(font,30),fill=(241,210,131))
d.text((24,68),'ORIGINAL NES',font=ImageFont.truetype(font,20),fill=(182,193,205));d.text((552,68),'HD REVIEW BUILD',font=ImageFont.truetype(font,20),fill=(241,210,131))
for i,(movie,n,title)in enumerate(scenes):
 y=110+i*500;d.text((24,y),title,font=ImageFont.truetype(font,18),fill=(216,226,234))
 for col,mode in enumerate(['original',a.mode]):
  im=Image.open(a.replays/movie/mode/'frames'/f'{n:05}.png').convert('RGB')
  if mode=='original':im=im.crop((0,8,256,232))
  im=im.resize((496,434),Image.Resampling.NEAREST if mode=='original'else Image.Resampling.LANCZOS)
  canvas.paste(im,(24+col*528,y+34))
d.text((24,canvas.height-30),'Matching emulator frames. Original movement, dialogue and game rules remain live.',font=ImageFont.truetype(font,15),fill=(156,173,184))
preview=a.output/'Bionic_Commando_HD_v0.8.0_Preview.png';canvas.save(preview)
allowed={'hires.txt','README.txt'}
for line in (r/'pack/hires.txt').read_text().splitlines():
 body=line.split(']',1)[-1]if line.startswith('[')else line
 if body.startswith('<img>'):allowed.add(body[5:])
 if body.startswith('<background>'):allowed.add(body[12:].split(',')[0])
assert {p.name for p in(r/'pack').iterdir()if p.is_file()}==allowed,'Unused or missing runtime file'
install=a.output/'Bionic_Commando_HD_v0.8.0.zip'
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for name in sorted(allowed):z.write(r/'pack'/name,name)
with zipfile.ZipFile(install)as z:assert z.testzip()is None
print(json.dumps([{'filename':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [install,preview]],indent=2))
