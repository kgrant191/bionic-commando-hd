"""Package the install files, reproducible source and actual-emulator preview."""
from pathlib import Path
import argparse, zipfile, json, hashlib
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser()
parser.add_argument('--screenshots',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
title_font=ImageFont.truetype(font_path,32)
small_font=ImageFont.truetype(font_path,17)
label_font=ImageFont.truetype(font_path,20)
canvas=Image.new('RGB',(1600,1120),(13,19,26));d=ImageDraw.Draw(canvas)
d.text((24,18),'BIONIC COMMANDO HD',font=title_font,fill=(241,210,131))
d.text((24,61),'v0.4.0  |  AREA 1 FEEDBACK FIXES  |  Actual MesenCE replay screenshots',font=small_font,fill=(182,193,205))
frames=[(2440,'EQUIPMENT / LIVE SELECTION'),(3705,'PAINTED SWING / STEEL ARM'),(7680,'SEARCHLIGHT / EXTERIOR'),
        (7965,'ENEMY CROUCH / FIRING — SAME ZOOM'),(8430,'WALL EDGES / SPENCER'),(21720,'TOWER / SPENCER')]
for i,(n,label) in enumerate(frames):
    x=16+(i%3)*528;y=104+(i//3)*500
    im=Image.open(args.screenshots/f'{n:05d}.png').convert('RGB')
    assert im.size==(1024,896)
    if n==3705:im=im.crop((420,330,740,610))
    if n==7680:im=im.crop((640,560,1024,896))
    if n==7965:
        pair=Image.new('RGB',(512,448),(13,19,26));pd=ImageDraw.Draw(pair)
        crouch=Image.open(args.screenshots/'08430.png').convert('RGB').crop((160,292,320,460))
        firing=im.crop((728,620,888,788))
        for col,(part,name)in enumerate([(crouch,'CROUCH'),(firing,'FIRING')]):
            pair.paste(part.resize((256,269),Image.Resampling.LANCZOS),(col*256,90))
            pd.text((col*256+12,58),name,font=small_font,fill=(216,226,234))
        im=pair
    canvas.paste(im.resize((512,448),Image.Resampling.LANCZOS),(x,y))
    d.text((x,y+458),label,font=label_font,fill=(216,226,234))
preview=args.output/'Bionic_Commando_HD_v0.4.0_Preview.png';canvas.save(preview)

install=args.output/'Bionic_Commando_HD_v0.4.0.zip'
allowed={'hires.txt','README.txt','title.png','radio.png','sky.png','tiles.png','worldmap.png','equipment.png'}|{f'portrait{i}.png'for i in range(10)}
assert {p.name for p in (root/'pack').iterdir()if p.is_file()}==allowed
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for name in sorted(allowed):z.write(root/'pack'/name,name)
with zipfile.ZipFile(install)as z:assert z.testzip()is None

source=args.output/'Bionic_Commando_HD_v0.4.0_Source.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for p in sorted(root.rglob('*')):
        if not p.is_file()or any(part in {'.git','__pycache__'}for part in p.relative_to(root).parts):continue
        assert p.suffix.lower()not in {'.nes','.mmo','.mss','.so','.dll','.dylib'}
        z.write(p,'bionic-commando-hd/'+str(p.relative_to(root)))
with zipfile.ZipFile(source)as z:assert z.testzip()is None
result=[{'filename':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in [install,preview,source]]
print(json.dumps(result,indent=2))
