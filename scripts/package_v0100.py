"""Package the installed runtime and a review sheet from actual emulator captures."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent;out=R/'output';out.mkdir(exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold=font.replace('.ttf','-Bold.ttf');title=ImageFont.truetype(bold,34);label=ImageFont.truetype(bold,23);small=ImageFont.truetype(font,19)
c=Image.new('RGB',(1240,1860),'#111d23');d=ImageDraw.Draw(c)
d.text((24,22),'Bionic Commando HD · v0.10.0',font=title,fill='#f2d9a2');d.text((24,66),'Weapon designs, damage corrections and Area 16 · Actual emulator captures',font=small,fill='#c5d7dc')
def shot(movie,mode,n):return Image.open(R/f'replay/{movie}/{mode}/frames/{n:05d}.png').convert('RGB')
def panel(i,name,im,note):
 x=24+(i%2)*608;y=110+(i//2)*572;d.text((x,y),name,font=label,fill='#f2d9a2');im=ImageOps.contain(im,(584,493),Image.Resampling.LANCZOS);c.paste(im,(x+(584-im.width)//2,y+38+(493-im.height)//2));d.text((x,y+538),note,font=small,fill='#b8cdd3')
panel(0,'Equipment menu',shot('issue1-enemy','release',13),'Rocket launcher and three-barrel wide cannon')
panel(1,'Rocket launcher',shot('16','ready',2671),'Large circular projectile · Original timing')
wide=shot('16','wide-release',2671).crop((450,540,720,820));panel(2,'Wide cannon · Equipped view',wide,'Three visible barrels · Test-selected weapon')
# Keep two independent captures clearly separated when showing small repairs.
details=Image.new('RGB',(584,493),'#142128');dd=ImageDraw.Draw(details)
a=shot('issue1-enemy','release',337).crop((490,410,650,590));b=shot('issue1-enemy','release',1609).crop((520,450,720,660))
for i,(im,caption)in enumerate([(a,'Damage state'),(b,'Dropped grenade')]):
 im=ImageOps.contain(im,(280,420),Image.Resampling.LANCZOS);details.paste(im,(i*292+(280-im.width)//2,30+(420-im.height)//2));dd.text((i*292+15,460),caption,font=small,fill='#d9e4e7')
panel(3,'Damage and grenade repairs',details,'HD artwork through the recorded states')
panel(4,'Area 16 · Exterior',shot('16','ready',3181),'Buildings, terrain, NPCs and equipped weapon')
panel(5,'Area 16 · Interior',shot('16','ready',4771),'Stone room, moving barrier and contact')
c.save(out/'Bionic_Commando_HD_v0.10.0_Preview.png')
pack=ROOT/'pack';path=out/'Bionic_Commando_HD_v0.10.0.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,9)as z:
 for p in sorted(pack.iterdir()):
  assert p.is_file()and p.suffix in {'.txt','.png'},p
  z.write(p,p.name)
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 assert len(z.namelist())==38
 for n in z.namelist():assert z.read(n)==(pack/n).read_bytes()
report={'version':'0.10.0','runtime_files':38,'runtime_zip_bytes':path.stat().st_size,'runtime_zip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'review_preview':'Actual emulator screenshots; labeled wide-cannon test and close-up crops.'}
(ROOT/'validation/v0100-delivery.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
