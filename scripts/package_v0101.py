"""Make the review ZIP, visual comparison and actual replay motion preview."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json,subprocess,zipfile

ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent;out=R/'output';out.mkdir(exist_ok=True)
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title=ImageFont.truetype(F.replace('.ttf','-Bold.ttf'),32)
label=ImageFont.truetype(F.replace('.ttf','-Bold.ttf'),23)
small=ImageFont.truetype(F,18)
def shot(movie,mode,n):return Image.open(R/f'replay/{movie}/{mode}/frames/{n:05}.png').convert('RGB')
c=Image.new('RGB',(1240,1660),'#132129');d=ImageDraw.Draw(c)
d.text((24,20),'Bionic Commando HD · v0.10.1',font=title,fill='#f4dba6')
d.text((24,65),'Actual emulator captures · Movement, scrolling buildings and dialogue',font=small,fill='#b8cdd1')
panels=[
 ('v0.10.0 · Hit flash',shot('issue1-enemy','release',613).crop((336,404,536,624))),
 ('v0.10.1 · Complete shoulder launcher',shot('issue1-enemy','v0101-final',613).crop((336,404,536,624))),
 ('v0.10.0 · Building edge',shot('16','ready',4351).crop((0,96,384,832))),
 ('v0.10.1 · Stable building edge',shot('16','v0101',4351).crop((0,96,384,832))),
 ('v0.10.0 · Contact dialogue',shot('16','ready',4891)),
 ('v0.10.1 · Same red-clothed contact',shot('16','v0101',4891)),
]
for i,(text,im)in enumerate(panels):
    x=24+i%2*608;y=108+i//2*506
    d.text((x,y),text,font=label,fill='#f4dba6')
    im=ImageOps.contain(im,(584,456),Image.Resampling.LANCZOS)
    c.paste(im,(x+(584-im.width)//2,y+35+(456-im.height)//2))
c.save(out/'Bionic_Commando_HD_v0.10.1_Preview.png')

path=out/'Bionic_Commando_HD_v0.10.1.zip';pack=ROOT/'pack'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,9)as z:
    for p in sorted(pack.iterdir()):
        assert p.is_file()and p.suffix in {'.txt','.png'}
        z.write(p,p.name)
with zipfile.ZipFile(path)as z:
    assert z.testzip()is None and len(z.namelist())==39
    for n in z.namelist():assert z.read(n)==(pack/n).read_bytes()

video=out/'Bionic_Commando_HD_v0.10.1_Motion_Preview.mp4'
cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1024x960','-r','60','-i','-','-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
segments=[('issue1-enemy','v0101-final',range(241,1801),'Spencer · Movement and damage flashes',1),
          ('16','v0101',range(3061,4412,3),'Area 16 · Stable scrolling buildings',3),
          ('16','v0101',range(4771,5012,3),'Area 16 · Red-clothed contact',3)]
count=0
for movie,mode,frames,caption,repeats in segments:
    for n in frames:
        im=Image.new('RGB',(1024,960),'#132129');im.paste(shot(movie,mode,n),(0,64))
        draw=ImageDraw.Draw(im);draw.text((20,10),'Bionic Commando HD v0.10.1',font=label,fill='#f4dba6')
        draw.text((20,39),caption,font=small,fill='#c4d9dd')
        data=im.tobytes()
        for _ in range(repeats):process.stdin.write(data);count+=1
process.stdin.close();assert process.wait()==0
report={'version':'0.10.1','runtime_files':39,'runtime_zip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'review_video_seconds':count/60,'review_video_source':'Actual emulator captures at original playback speed; 60 fps overhead and 20 fps town samples repeated to 60 fps.',
        'comparison_source':'Actual v0.10.0 and v0.10.1 emulator captures.'}
(ROOT/'validation/v0101-delivery.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
