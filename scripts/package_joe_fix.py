"""Package the focused v0.8.2 fix with actual before/after emulator crops."""
from pathlib import Path
import argparse, zipfile
from PIL import Image, ImageDraw, ImageFont
p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[1];a.output.mkdir(parents=True,exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
preview=Image.new('RGB',(760,588),(16,23,29));d=ImageDraw.Draw(preview)
d.text((24,16),'SUPER JOE — REAR FOOT FIX',font=ImageFont.truetype(font,25),fill=(237,212,160))
d.text((24,55),'Before / v0.8.1',font=ImageFont.truetype(font,18),fill=(193,202,206))
d.text((392,55),'After / v0.8.2',font=ImageFont.truetype(font,18),fill=(193,202,206))
for x,path in [(24,a.before),(392,a.after)]:
    im=Image.open(path).convert('RGB').crop((552,304,728,544)).resize((344,469),Image.Resampling.NEAREST)
    preview.paste(im,(x,87))
d.text((24,565),'Actual emulator frames; same artwork, size and position.',font=ImageFont.truetype(font,13),fill=(166,181,187))
preview.save(a.output/'Bionic_Commando_HD_v0.8.2_Preview.png')
allowed={'hires.txt','README.txt'}
for line in (r/'pack/hires.txt').read_text().splitlines():
    body=line.split(']',1)[-1]if line.startswith('[')else line
    if body.startswith('<img>'):allowed.add(body[5:])
    if body.startswith('<background>'):allowed.add(body[12:].split(',')[0])
assert {p.name for p in(r/'pack').iterdir()if p.is_file()}==allowed
path=a.output/'Bionic_Commando_HD_v0.8.2.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for name in sorted(allowed):z.write(r/'pack'/name,name)
with zipfile.ZipFile(path)as z:assert z.testzip()is None
print(path)
