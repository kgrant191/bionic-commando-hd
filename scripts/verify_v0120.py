"""Area 3 exact-ZIP replay, every-frame coverage and previous-area isolation."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json,re
from PIL import Image
from verify_v0110 import structure
from verify_v0112 import verify_bounds as area2_bounds
ROOT=Path(__file__).resolve().parents[1]

def scope(pack,baseline):
 old=(baseline/'hires.txt').read_text().splitlines();new=(pack/'hires.txt').read_text().splitlines()
 before=Counter(s for s in old if '<tile>'in s);after=Counter(s for s in new if '<tile>'in s)
 assert not before-after,'Earlier-area tile rules changed'
 extra=list((after-before).elements())
 for s in extra:
  assert s.startswith('[') and 'area3' in s[1:].split(']',1)[0].split('&'),s
 images=0
 for p in baseline.glob('*.png'):
  assert p.read_bytes()==(pack/p.name).read_bytes(),p.name;images+=1
 # A condition must be declared before a background/rule references it.
 names={'hmirror','vmirror'};old_lines=set(old)
 for s in new:
  if s.startswith('<condition>'):names.add(s[11:].split(',')[0])
  if s not in old_lines and s.startswith('['):
   for term in s[1:].split(']',1)[0].split('&'):assert term.lstrip('!')in names,term
 return {'existing_tile_rules_unchanged':sum(before.values()),'existing_pngs_unchanged':images,'new_area3_rules':len(extra),'new_rules_all_area3_scoped':True,'condition_declaration_order_valid':True}

def bounds(pack):
 definitions={};lines=(pack/'hires.txt').read_text().splitlines();checked=0
 for s in lines:
  if s.startswith('<condition>'):
   a=s[11:].split(',');definitions[a[0]]=a[1:]
 for s in lines:
  if not(s.startswith('[')and'<tile>'in s):continue
  terms=s[1:].split(']',1)[0].split('&')
  if 'area3'not in terms:continue
  rect={'X':[0,255],'Y':[0,239]}
  for name in terms:
   d=definitions.get(name)
   if not d:continue
   if d[0]in['positionCheckX','positionCheckY']:
    axis,op,v=d[0][-1],d[1],int(d[2])
    if op=='>=':rect[axis][0]=max(rect[axis][0],v)
    elif op=='<':rect[axis][1]=min(rect[axis][1],v-1)
   elif d[0]in['tileNearby','spriteNearby']:
    hs=[True]if'hmirror'in terms else[False]if'!hmirror'in terms else[False,True]
    vs=[True]if'vmirror'in terms else[False]if'!vmirror'in terms else[False,True]
    if d[0]=='tileNearby':hs,vs=[False],[False]
    for h in hs:
     for v in vs:
      dx,dy=int(d[1])*(-1 if h else 1),int(d[2])*(-1 if v else 1)
      for x in rect['X']:
       for y in rect['Y']:assert 0<=x+dx<256 and 0<=y+dy<240,(name,x,y,dx,dy)
    checked+=1
 assert checked>0
 return {'area3_bounded_neighbor_references':checked,'unsafe_references':0,'preserved_area2_bounds':area2_bounds(pack)}

def replay(pack,original,result):
 frames=11110
 assert int((result/'home/done').read_text())==frames
 checkpoints=sorted((original/'frames').glob('*.ram'))
 assert {int(p.stem)for p in checkpoints}=={1,frames}|set(range(60,frames+1,60))
 for p in checkpoints:
  for suffix in['.ram','.ppu']:assert p.with_suffix(suffix).read_bytes()==(result/'frames'/p.with_suffix(suffix).name).read_bytes(),(p,suffix)
 loaded=result/'home/HdPacks/Bionic Commando (USA)'
 assert {p.name for p in pack.iterdir()}=={p.name for p in loaded.iterdir()}
 for p in pack.iterdir():assert p.read_bytes()==(loaded/p.name).read_bytes(),p.name
 log=(result/'log.txt').read_text()
 assert log.count('Screen guard begins at ')==2 and 'Guarded playback fault'not in log
 assert not re.search(r'\[HDPack\].*(?:error|invalid|unable)|script error|Exception',log,re.I)
 rows=list(csv.DictReader((result/'home/audit.tsv').open(),delimiter='\t'));missing=[r for r in rows if r['rule']=='-1'];assert not missing,missing
 return {'movie_input_frames':frames,'ram_checkpoints':len(checkpoints),'ppu_checkpoints':len(checkpoints),'state_mismatches':0,'audited_graphics_states':len(rows),'uncovered_graphics_states':0,'loaded_pack_matches_extracted_zip':True,'guarded_single_attempt_completed':True,'screenshots':len(list((result/'frames').glob('*.png')))}

def main():
 ap=argparse.ArgumentParser()
 for a in['pack','baseline','original','replay']:ap.add_argument('--'+a,type=Path,required=True)
 a=ap.parse_args();report={'scope':scope(a.pack,a.baseline),'structure':structure(a.pack),'bounds':bounds(a.pack),'playback':replay(a.pack,a.original,a.replay)}
 (ROOT/'validation/v0120-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
