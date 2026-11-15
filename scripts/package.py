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
canvas=Image.new('RGB',(1360,3168),(13,19,26));d=ImageDraw.Draw(canvas)
d.text((24,18),'BIONIC COMMANDO HD — v0.6.1',font=title_font,fill=(241,210,131))
d.text((24,66),'v0.5.0 — BEFORE',font=label_font,fill=(182,193,205))
d.text((696,66),'v0.6.1 — AFTER',font=label_font,fill=(241,210,131))
comparisons=[(2040,None,'AREA 13 — OUTPOST BUILDINGS AND ROCKY BANKS'),
             (3960,None,'NEUTRAL-AREA CONTACT AND LIVE MOVEMENT'),
             (2160,None,'NEW DIALOGUE PORTRAITS — LIVE TEXT AND TALKING'),
             (4680,None,'STONE INTERIOR AND FIRST-AID PICKUP'),
             (5880,None,'WHITE GUARDS, PARACHUTES AND ALARM PALETTE')]

for row,(n,box,label)in enumerate(comparisons):
    y=118+row*600
    for col,folder in enumerate([args.before,args.screenshots]):
        im=Image.open(folder/f'{n:05d}.png').convert('RGB');assert im.size==(1024,896)
        if box:im=im.crop(box)
        canvas.paste(im.resize((640,560),Image.Resampling.LANCZOS),(24+col*672,y))
    d.text((24,y+572),label,font=label_font,fill=(216,226,234))
d.text((24,3136),'Actual MesenCE replay screenshots • Matching frames, crop and zoom',font=small_font,fill=(156,173,184))
preview=args.output/'Bionic_Commando_HD_v0.6.1_Preview.png';canvas.save(preview)

install=args.output/'Bionic_Commando_HD_v0.6.1.zip'
allowed={'hires.txt','README.txt','title.png','radio.png','sky.png','tiles.png','worldmap.png','equipment.png','area-clear.png'}|{f'portrait{i}.png'for i in range(10)}
assert {p.name for p in (root/'pack').iterdir()if p.is_file()}==allowed
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for name in sorted(allowed):z.write(root/'pack'/name,name)
with zipfile.ZipFile(install)as z:assert z.testzip()is None

source=args.output/'Bionic_Commando_HD_v0.6.1_Source.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for p in sorted(root.rglob('*')):
        if not p.is_file()or any(part in {'.git','__pycache__'}for part in p.relative_to(root).parts):continue
        assert p.suffix.lower()not in {'.nes','.mmo','.mss','.so','.dll','.dylib'}
        z.write(p,'bionic-commando-hd/'+str(p.relative_to(root)))
with zipfile.ZipFile(source)as z:assert z.testzip()is None
result=[{'filename':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in [install,preview,source]]
print(json.dumps(result,indent=2))
