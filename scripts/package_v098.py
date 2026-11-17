"""Package the tested runtime and a head-aligned before/after animation."""
from pathlib import Path
import json,zipfile,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent;out=R/'deliverables';out.mkdir(exist_ok=True)
H='C7C7C7D7C7C7C7FF4141796979797979'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
title=ImageFont.truetype(bold,27);label=ImageFont.truetype(bold,23);small=ImageFont.truetype(font,17)
a=np.array(Image.open(ROOT/'validation/v098-composite-0.png'));b=np.array(Image.open(ROOT/'validation/v098-composite-1.png'))
hardware=np.all(a==b,axis=2)&(a[:,:,3]==255);mismatches=0;phases=set()
movie=out/'Bionic_Commando_HD_v0.9.8_Thruster_Preview.mp4'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1120x560','-r','60','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE);images=[]
for n in range(950,1066):
 entries=[s.split(',')for s in(R/f'replay/8/before/tiles/{n-1:05d}.tiles').read_text().splitlines()]
 h=next(e for e in entries if e[0]=='1'and e[3]==H);x,y=map(int,h[1:3]);pal=int(h[4])
 phase=next(e[3]for e in entries if e[0]=='1'and int(e[1])==x+24 and int(e[2])==y+24);phases.add(phase)
 expected=a[:,:,:3].copy()
 if pal!=0xFF30150F:expected=np.clip(expected.astype(float)*1.1,0,255).astype('uint8')
 actual=Image.open(R/f'replay/8/v098-animation/frames/{n:05d}.png').convert('RGB')
 patch=np.array(actual.crop(((x+16)*4,(y+8)*4,(x+48)*4,(y+40)*4)))
 mismatches+=int((np.any(expected!=patch,axis=2)&hardware).sum())
 canvas=Image.new('RGB',(1120,560),'#101c22');d=ImageDraw.Draw(canvas)
 d.text((24,16),'Bionic Commando HD — Area 5 thruster correction',font=title,fill='#efdaa9')
 for j,(mode,name)in enumerate([('v097-animation','Before · v0.9.7'),('v098-animation','Fixed · v0.9.8')]):
  d.text((j*560+24,62),name,font=label,fill='#cbdce0')
  im=Image.open(R/f'replay/8/{mode}/frames/{n:05d}.png').convert('RGB').crop(((x-48)*4,(y-24)*4,(x+56)*4,(y+56)*4)).resize((520,400),Image.Resampling.LANCZOS)
  canvas.paste(im,(j*560+20,99))
 d.text((24,519),'Actual emulator captures • Boss aligned for comparison • Fixed housing, animated flame',font=small,fill='#b4cbd1')
 images.append(canvas.tobytes())
 if n==1020:canvas.save(out/'Bionic_Commando_HD_v0.9.8_Preview.png')
for loop in range(3):
 for frame in images:p.stdin.write(frame)
p.stdin.close();assert p.wait()==0
assert mismatches==0 and len(phases)==2
report={'consecutive_animation_frames_checked':116,'opaque_hardware_pixels_checked_per_frame':int(hardware.sum()),'hardware_pixel_mismatches':mismatches,'native_flame_phases_seen':2,'preview_loops':3,'alignment':'Boss head aligned; captured game animation remains at 60 fps.'}
(ROOT/'validation/v098-animation.json').write_text(json.dumps(report,indent=2)+'\n')
pack=ROOT/'pack';zpath=out/'Bionic_Commando_HD_v0.9.8.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,9)as z:
 for f in sorted(pack.iterdir()):
  if f.is_file():z.write(f,f.name)
with zipfile.ZipFile(zpath)as z:
 assert z.testzip()is None
 for name in z.namelist():assert z.read(name)==(pack/name).read_bytes()
print(json.dumps({'runtime_files':len(list(pack.iterdir())),'zip_bytes':zpath.stat().st_size,'zip_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'animation':report},indent=2))
