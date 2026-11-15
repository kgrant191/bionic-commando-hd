"""Package playable files and a replay-based before/after review image."""
from pathlib import Path
import argparse,zipfile,json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
from area1_feedback import POW,FLASK

parser=argparse.ArgumentParser()
parser.add_argument('--screenshots',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--before',type=Path,required=True)
parser.add_argument('--feedback-before',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
canvas=Image.new('RGB',(1360,1430),(13,19,26));d=ImageDraw.Draw(canvas)
d.text((24,18),'BIONIC COMMANDO HD — v0.7.6',font=ImageFont.truetype(font,32),fill=(241,210,131))
d.text((24,68),'v0.7.5 — BEFORE',font=ImageFont.truetype(font,20),fill=(182,193,205))
d.text((696,68),'v0.7.6 — AFTER',font=ImageFont.truetype(font,20),fill=(241,210,131))
comparisons=[(1,10800,(500,444,684,620),'AREA 1 — CLEAN OPEN DOORFRAME'),
             (7,300,(640,482,784,630),'BAZOOKA SOLDIER — COMPLETE GRENADE RELEASE POSE'),
             (7,60,(568,384,688,484),'POW — UPDATED ORBITING STAR THROUGH EXPIRY')]
for row,(movie,n,box,label)in enumerate(comparisons):
 y=112+row*310;d.text((24,y),label,font=ImageFont.truetype(font,20),fill=(216,226,234))
 before=args.feedback_before/f'{n:05d}.png'if movie==7 else args.before/f'replay{movie}/frames/{n:05d}.png'
 after=args.screenshots/f'replay{movie}/frames/{n:05d}.png'
 for col,path in enumerate([before,after]):
  im=Image.open(path).convert('RGB').crop(box);im.thumbnail((640,244),Image.Resampling.LANCZOS)
  factor=min(640/im.width,244/im.height);im=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS)
  x=24+col*672;d.rounded_rectangle((x,y+34,x+640,y+284),radius=6,fill=(24,35,43));canvas.paste(im,(x+(640-im.width)//2,y+36+(244-im.height)//2))
# Item panels assemble the native sprite quadrants, including live mirroring.
import numpy as np,re
pal=[int(h,16)for h in re.findall('0x([A-Fa-f0-9]+)',(root/'tools/palette.inc').read_text())]
lines=(root/'pack/hires.txt').read_text().splitlines();atlas=Image.open(root/'pack/tiles.png').convert('RGBA')
def tile(k,hd):
 if hd:
  l=next(l for l in lines if '<tile>0,'+k+',FF202A0F,'in l and l.startswith('[!title&!worldmap&!equipment&!radio&!areaClear]'))
  a=l.split('<tile>')[1].split(',');x,y=map(int,a[3:5]);return atlas.crop((x,y,x+32,y+32))
 bits=np.unpackbits(np.frombuffer(bytes.fromhex(k),dtype=np.uint8)).reshape(16,8);ix=bits[:8]+2*bits[8:];colors=[[0,0,0,0]]+[[(pal[c]>>16)&255,(pal[c]>>8)&255,pal[c]&255,255]for c in [0x20,0x2A,0x0F]]
 return Image.fromarray(np.array(colors,dtype='uint8')[ix]).resize((32,32),Image.Resampling.NEAREST)
y=1042;d.text((24,y),'CRATE REWARDS — POW AND RECOVERY FLASK (MAPPED TILE ASSEMBLIES)',font=ImageFont.truetype(font,20),fill=(216,226,234))
for col in range(2):
 x=24+col*672;d.rounded_rectangle((x,y+34,x+640,y+284),radius=6,fill=(24,35,43))
 for item,ks in enumerate([POW,FLASK]):
  a=Image.new('RGBA',(64,64))
  for i,k in enumerate(ks):
   t=tile(k,col==1)
   if item==0:a.alpha_composite(t,(i%2*32,i//2*32))
   else:a.alpha_composite(t,(0,i*32));a.alpha_composite(ImageOps.mirror(t),(32,i*32))
  a=a.resize((192,192),Image.Resampling.NEAREST);canvas.paste(a,(x+64+item*310,y+55),a)
d.text((24,1360),'Top three rows: matching emulator frames. Bottom row: original patterns and their HD tile replacements.',font=ImageFont.truetype(font,16),fill=(156,173,184))
d.text((24,1390),'The game still controls movement, flashes, item behavior, hit detection and effect lifetime.',font=ImageFont.truetype(font,16),fill=(156,173,184))
preview=args.output/'Bionic_Commando_HD_v0.7.6_Preview.png';canvas.save(preview)
install=args.output/'Bionic_Commando_HD_v0.7.6.zip'
allowed={'hires.txt','README.txt','title.png','radio.png','sky.png','tiles.png','worldmap.png','equipment.png','area-clear.png','area4-distance.png','area4-boss0.png','area4-boss1.png','area13-distance.png','area13-distance-alert.png','area13-distance-flash.png'}|{f'portrait{i}.png'for i in range(10)}
assert {p.name for p in(root/'pack').iterdir()if p.is_file()}==allowed
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for name in sorted(allowed):z.write(root/'pack'/name,name)
with zipfile.ZipFile(install)as z:assert z.testzip()is None
print(json.dumps([{'filename':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [install,preview]],indent=2))
