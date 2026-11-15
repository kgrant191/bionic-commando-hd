"""Package the install files, reproducible source and actual-emulator preview."""
from pathlib import Path
import argparse, zipfile, json, hashlib
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser()
parser.add_argument('--screenshots',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--before',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
title_font=ImageFont.truetype(font_path,32)
small_font=ImageFont.truetype(font_path,17)
label_font=ImageFont.truetype(font_path,20)
# Each panel is cropped from an actual emulator replay at the same frame.
canvas=Image.new('RGB',(1360,2400),(13,19,26));d=ImageDraw.Draw(canvas)
d.text((24,18),'BIONIC COMMANDO HD — v0.7.3',font=title_font,fill=(241,210,131))
d.text((24,68),'v0.7.2 — BEFORE',font=label_font,fill=(182,193,205))
d.text((696,68),'v0.7.3 — AFTER',font=label_font,fill=(241,210,131))
comparisons=[
 (4,1800,(666,154,920,478),'RED CONTACT — IN-PERSON PORTRAIT AND MATCHING UNIFORM'),
 (4,4200,(704,146,960,472),'GREEN CONTACT — IN-PERSON PORTRAIT AND CLEAN FRAME'),
 (4,2138,(696,154,956,476),'WHITE CONTACT — REMOVE THE SECOND PORTRAIT'),
 (4,2520,(116,568,784,804),'SUPPLY ROOM — COMPLETE DOORWAY AND MATCHING SPIKE BASES'),
 (4,2040,(0,0,1024,896),'TOWN — PAINTED SKY, CLOUDS, MOUNTAINS AND TREES'),
 (4,1320,(176,560,464,748),'TOWN — PAINTED BARRED BUILDING FAÇADES')]
for row,(movie,n,box,label)in enumerate(comparisons):
    y=112+row*368
    d.text((24,y),label,font=label_font,fill=(216,226,234))
    for col,folder in enumerate([args.before,args.screenshots]):
        im=Image.open(folder/f'replay{movie}'/'frames'/f'{n:05d}.png').convert('RGB').crop(box)
        im.thumbnail((640,292),Image.Resampling.LANCZOS)
        x=24+col*672
        d.rounded_rectangle((x,y+34,x+640,y+330),radius=6,fill=(24,35,43))
        canvas.paste(im,(x+(640-im.width)//2,y+36+(292-im.height)//2))
d.text((24,2360),'Actual MesenCE replays • Matching frames and crops • Native animation timing and game state retained',font=small_font,fill=(156,173,184))
preview=args.output/'Bionic_Commando_HD_v0.7.3_Preview.png';canvas.save(preview)

install=args.output/'Bionic_Commando_HD_v0.7.3.zip'
allowed={'hires.txt','README.txt','title.png','radio.png','sky.png','tiles.png','worldmap.png','equipment.png','area-clear.png','area4-distance.png','area4-boss0.png','area4-boss1.png','area13-distance.png','area13-distance-alert.png','area13-distance-flash.png'}|{f'portrait{i}.png'for i in range(10)}
assert {p.name for p in (root/'pack').iterdir()if p.is_file()}==allowed
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for name in sorted(allowed):z.write(root/'pack'/name,name)
with zipfile.ZipFile(install)as z:assert z.testzip()is None

source=args.output/'Bionic_Commando_HD_v0.7.3_Source.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for p in sorted(root.rglob('*')):
        if not p.is_file()or any(part in {'.git','__pycache__'}for part in p.relative_to(root).parts):continue
        assert p.suffix.lower()not in {'.nes','.mmo','.mss','.so','.dll','.dylib'}
        z.write(p,'bionic-commando-hd/'+str(p.relative_to(root)))
with zipfile.ZipFile(source)as z:assert z.testzip()is None
result=[{'filename':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in [install,preview,source]]
print(json.dumps(result,indent=2))
