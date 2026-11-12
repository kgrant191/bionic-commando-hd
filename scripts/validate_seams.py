"""Compare the targeted doorway/seam patch against the saved v0.4.0 atlas."""
from pathlib import Path
from PIL import Image
import subprocess,io,json,numpy as np
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--before-ref',default='c8bf62f8f962cccf2ce09fae875749f995bb975e');args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
def read_atlas(txt,im):
 out={}
 for l in txt.splitlines():
  body=l.split(']',1)[-1]
  if not body.startswith('<tile>'):continue
  a=body[6:].split(',');x,y=int(a[3]),int(a[4]);condition=l[:l.index(']')+1]if l.startswith('[')else''
  out[(condition,a[1],a[2])]=np.array(im.crop((x,y,x+32,y+32)))
 return out
oldtxt=subprocess.check_output(['git','show',args.before_ref+':pack/hires.txt'],cwd=root).decode()
oldimg=Image.open(io.BytesIO(subprocess.check_output(['git','show',args.before_ref+':pack/tiles.png'],cwd=root)))
old=read_atlas(oldtxt,oldimg);new=read_atlas((root/'pack/hires.txt').read_text(),Image.open(root/'pack/tiles.png'))
assert old.keys()==new.keys()
rep=json.load(open(root/'validation/seam_mapping.json'));doors={tuple(x)for x in rep['door_patterns']};seams={ (x['key'],x['palette'])for x in rep['repairs']};changed=[]
for k in old:
 if not np.array_equal(old[k],new[k]):
  assert not k[0],k
  assert k[1:]in doors|seams,k
  changed.append(k[1:])
  if k[1:]in seams:assert np.array_equal(old[k][:,:,3],new[k][:,:,3]),'Native aperture changed'
wkeys=set()
for l in (root/'capture/02640.tiles').read_text().splitlines():
 a=l.split(',')
 if a[0]=='0' and int(a[4])==0x0F302118 and int(a[2])>=208:wkeys.add(a[3])
assert all(np.array_equal(old[k],new[k])for k in old if k[1]in wkeys)
blue_pixels=0
for k,v in new.items():
 if k[0] or k[2]!='0F271505':continue
 rgb=v[:,:,:3].astype(float);blue=(rgb[:,:,2]>rgb[:,:,0]*1.15)&(rgb[:,:,2]>rgb[:,:,1]*.88)&(rgb[:,:,2]-rgb[:,:,0]>22)&(rgb[:,:,2]>80)&(v[:,:,3]>0)
 blue_pixels+=int(blue.sum())
assert blue_pixels==0,blue_pixels
report={'opaque_blue_structural_pixels':blue_pixels,'version':'0.4.1','tile_rules_compared':len(old),'changed_patterns':changed,'unrelated_tiles_changed':0,'structural_transparency_preserved':True,'water_unchanged':True,'door_keys':len(doors),'seam_keys':len(seams)}
(root/'validation/door-seams-v0.4.1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
