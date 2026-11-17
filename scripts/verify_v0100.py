"""Validate the new runtime against locally supplied replay captures."""
from pathlib import Path
import argparse,hashlib,json,re
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--replay-root',type=Path,default=ROOT.parent/'replay');args=ap.parse_args();R=args.replay_root
pack=ROOT/'pack';lines=(pack/'hires.txt').read_text().splitlines();images=[];names=set();known=set();adds=[];fallbacks=set();tile_count=0
for l in lines:
 if l.startswith('<img>'):images.append(Image.open(pack/l[5:]))
 if l.startswith('<condition>'):
  n=l[11:].split(',')[0];assert n not in names,n;names.add(n)
 if l.startswith('['):
  for n in re.split('[&|!()]',l[1:].split(']')[0]):assert not n or n in names,n
 if '<background>'in l:
  f=l.split('<background>')[1].split(',')[0];assert Image.open(pack/f).size==(1024,960)
 if '<tile>'in l:
  a=l.split('<tile>')[1].split(',');i,x,y=int(a[0]),int(a[3]),int(a[4]);assert 0<=i<len(images)and x>=0 and y>=0 and x+32<=images[i].width and y+32<=images[i].height
  assert re.fullmatch('[0-9A-F]{32}',a[1])and re.fullmatch('[0-9A-F]{8}',a[2]);known.add(tuple(a[1:3]));tile_count+=1
  if l.startswith('<tile>'):fallbacks.add(tuple(a[1:3]))
 if l.startswith('<addition>'):adds.append(tuple(l[10:].split(',')))
assert len({a[:4]+a[6:]for a in adds})==len(adds)
assert all(tuple(a[:2])in known and tuple(a[4:6])in fallbacks for a in adds)
observed=set(map(tuple,json.loads((ROOT/'capture/v0100/observed-keys.json').read_text())));assert observed<=known
for p in (ROOT/'baselines/v098').iterdir():
 if p.name not in {'hires.txt','README.txt'}:assert p.read_bytes()==(pack/p.name).read_bytes(),p.name
results={}
for movie,hd,original,frames,selection in [('issue1-enemy','release','original',2010,None),('16','ready','original',7792,None),('16','wide-release','wide-original',2800,2),('regression-boss','ready','before',1940,None)]:
 d=R/movie/hd;src=R/movie/original;expected={1,frames}|set(range(30,frames+1,30));actual={int(p.stem)for p in(d/'frames').glob('*.ram')};assert actual==expected,(movie,actual^expected)
 assert frames<=int((d/'home/done').read_text())<=frames+2
 for n in sorted(expected):
  for ext in ['ram','ppu']:
   f=f'{n:05d}.{ext}';assert(d/'frames'/f).read_bytes()==(src/'frames'/f).read_bytes(),(movie,f)
 log=(d/'log.txt').read_text();assert 'HD enabled: 1'in log
 assert not re.search(r'\[HDPack\].*(?:error|invalid|unable)|script error|Exception',log,re.I)
 installed=d/'home/HdPacks/Bionic Commando (USA)'
 assert all(p.read_bytes()==(installed/p.name).read_bytes()for p in pack.iterdir()if p.name!='README.txt'),movie
 shots=[p for p in(d/'frames').glob('*.png')if p.stat().st_size>100]
 assert all(Image.open(p).size==(1024,896)for p in shots)
 result={'movie_frames':frames,'ram_and_ppu_checkpoints':len(expected),'ram_mismatches':0,'ppu_mismatches':0,'captured_screenshots':len(shots),'HD_loader_errors':0}
 if selection is not None:result['test_only_forced_equipment_value']=selection
 if movie=='regression-boss':
  for p in shots:assert np.array_equal(np.array(Image.open(p)),np.array(Image.open(src/'frames'/p.name))),p.name
  result['screenshots_identical_to_v098']=len(shots)
 results[movie+'/'+hd]=result
report={'version':'0.10.0','recordings':results,'tile_rules':tile_count,'conditions':len(names),'duplicate_addition_anchors':0,'observed_key_palette_pairs_with_rules':len(observed),'observed_pairs_without_rules':0,'prior_image_assets_unchanged':True,'pack_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(pack.iterdir())},'limits':'Full movies replayed with RAM/PPU sampled every 30 frames plus endpoints. Visual review is sampled, not exhaustive; key coverage alone does not prove every conditional rule matched. Wide-cannon mode uses a test-only equipment-selection override, excluded from the runtime. Unrecorded areas and states remain untested.'}
(ROOT/'validation/v0100-replay.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='pack_sha256'},indent=2))
