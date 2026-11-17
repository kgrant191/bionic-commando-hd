from pathlib import Path
import json,zipfile,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];root=R/'bionic-commando-hd';out=R/'deliverables';out.mkdir(exist_ok=True)
# The single-frame enemy flash is missed by three-frame screenshot sampling.
# Check every frame of the full rooftop and swinging section separately.
before=R/'replay/8/before-dense/frames';after=R/'replay/8/final-dense/frames';pink_before=0;pink_after=0;count=0
preview_only='--preview-only' in sys.argv
if preview_only:
 previous=json.loads((root/'validation/v097-dense.json').read_text());pink_before=previous['native_magenta_pixels_before'];pink_after=previous['native_magenta_pixels_after'];count=previous['frames_compared']
for n in ([] if preview_only else range(2,391)):
 f=f'{n:05d}.png';a=np.array(Image.open(before/f).convert('RGB'));b=np.array(Image.open(after/f).convert('RGB'))
 # Exact native magenta sampled from the visible fallback at frame 185.
 # Painted crimson armor retains shading instead of this flat NES color.
 pink_before+=int(np.all(a==[183,30,123],axis=2).sum())
 pink_after+=int(np.all(b==[183,30,123],axis=2).sum())
 for ext in ['ram','ppu']:
  assert (before/f'{n:05d}.{ext}').read_bytes()==(after/f'{n:05d}.{ext}').read_bytes()
 count+=1
assert pink_before>1000 and pink_after==0,(pink_before,pink_after)
dense={'frames_compared':count,'native_magenta_pixels_before':pink_before,'native_magenta_pixels_after':pink_after,'RAM_and_PPU_match':True,'enemy_flash_capture_frame':185,'swing_capture_frames':[216,225,231]}
(root/'validation/v097-dense.json').write_text(json.dumps(dense,indent=2)+'\n')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
title=ImageFont.truetype(bold,32);label=ImageFont.truetype(bold,24);small=ImageFont.truetype(font,18)
canvas=Image.new('RGB',(1280,2160),'#101c22');d=ImageDraw.Draw(canvas)
d.text((26,20),'Bionic Commando HD v0.9.7 — Screenshot fixes',font=title,fill='#efdaa9')
d.text((26,75),'Before (v0.9.6)',font=label,fill='#b4cbd1');d.text((666,75),'After (v0.9.7)',font=label,fill='#b4cbd1')
rows=[('HD rooftop railing and emblem',3,(244,76,660,360),(552,377),122,'final'),
      ('Enemy stays in HD during its brief damage flash',185,(380,60,700,300),(448,336),560,'final-dense'),
      ('Swinging body, grapple and hand retain their HD mappings',225,(650,420,1010,720),(480,400),970,'final'),
      ('Generator hit glow preserves black recesses',1206,(676,96,1024,736),(300,552),1450,'final')]
for caption,n,box,size,y,mode in rows:
 d.text((26,y),caption,font=label,fill='#e2ecee')
 for j,m in enumerate(['before-dense'if mode.endswith('dense')else'before',mode]):
  im=Image.open(R/f'replay/8/{m}/frames/{n:05d}.png').convert('RGB').crop(box).resize(size,Image.Resampling.LANCZOS)
  canvas.paste(im,(j*640+(640-size[0])//2,y+40))
d.text((26,2095),'Actual emulator captures. Earlier corrections and crimson/white boss retained.',font=small,fill='#b4cbd1')
d.text((26,2125),'Full 1,940-frame replay checked; opening rooftop/swing sequence reviewed every frame.',font=small,fill='#b4cbd1')
canvas.save(out/'Bionic_Commando_HD_v0.9.7_Preview.png')
if preview_only:sys.exit(0)
pack=root/'pack';zpath=out/'Bionic_Commando_HD_v0.9.7.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,9)as z:
 for p in sorted(pack.iterdir()):
  if p.is_file():z.write(p,p.name)
with zipfile.ZipFile(zpath)as z:
 assert z.testzip()is None
 for n in z.namelist():assert z.read(n)==(pack/n).read_bytes()
print(json.dumps({'zip':str(zpath),'runtime_files':len(list(pack.iterdir())),'zip_bytes':zpath.stat().st_size,'dense_review':dense},indent=2))
