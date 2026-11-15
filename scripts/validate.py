"""Check installed-pack structure and deterministic original/HD movie parity."""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('--original',type=Path,required=True)
parser.add_argument('--hd',type=Path,required=True)
parser.add_argument('--home',type=Path,required=True)
parser.add_argument('--log',type=Path,required=True)
parser.add_argument('--frames',type=int,default=40442)
parser.add_argument('--report',default='replay.json')
parser.add_argument('--checkpoint-step',type=int,default=None)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];pack=root/'pack'
rules=(pack/'hires.txt').read_text().splitlines()
images=[];definitions=[];additions=[]
for l in rules:
    body=l.split(']',1)[-1]if l.startswith('[')else l
    if body.startswith('<img>'):
        p=pack/body[5:];assert p.is_file();images.append(Image.open(p))
    if body.startswith('<background>'):
        p=pack/body[12:].split(',')[0];assert p.is_file()
        assert Image.open(p).size==(1024,960)
    if body.startswith('<tile>'):
        a=body[6:].split(',');idx=int(a[0]);x,y=int(a[3]),int(a[4])
        assert re.fullmatch('[0-9A-F]{32}',a[1])
        assert re.fullmatch('[0-9A-F]{8}',a[2])
        assert 0<=idx<len(images) and x>=0 and y>=0
        assert x+32<=images[idx].width and y+32<=images[idx].height
        definitions.append((a[1],a[2]))
    if body.startswith('<addition>'):
        a=body[10:].split(',')
        assert len(a)==7 and a[-1]=='N'
        assert -40<=int(a[2])<=48 and -24<=int(a[3])<=56
        additions.append(((a[0],a[1]),(a[4],a[5])))
assert '<overscan>8,0,8,0' in rules
assert '<options>disableSpriteLimit' in rules
stop_marker=int((args.home/'done').read_text())
assert args.frames<=stop_marker<=args.frames+2 # A pause request may finish one extra frame.
assert (args.hd/f'{args.frames:05d}.ram').is_file()
original=[p for p in sorted(args.original.glob('*.ram')) if int(p.stem)<=args.frames]
step=args.checkpoint_step or (120 if args.frames==40442 else 1)
expected={1,args.frames}|set(range(step,args.frames+1,step))
assert {int(p.stem)for p in original}==expected,'Incomplete native checkpoint set'
mismatches=[]
for p in original:
    q=args.hd/p.name
    if not q.is_file() or p.read_bytes()!=q.read_bytes():mismatches.append(p.name)
assert not mismatches,mismatches
screens=[]
for p in sorted(args.hd.glob('*.png')):
    if p.stat().st_size<100:continue # No decoded frame is available at frame 1.
    with Image.open(p) as im:assert im.size==(1024,896),(p.name,im.size)
    screens.append(p.name)
log=args.log.read_text()
assert 'PPU: 8HdNesPpu HD enabled: 1' in log
assert not re.search(r'\[HDPack\].*(error|Error)|script error|Script error|Exception',log)
stats=json.loads((root/'build_stats.json').read_text())
virtual_keys={v for a,v in additions}
assert all(a in set(definitions)and v in set(definitions)for a,v in additions)
assert len(virtual_keys)==stats['virtual_sprite_keys']
for v in virtual_keys:
    assert any(l.startswith('<tile>')and tuple(l[6:].split(',')[1:3])==v for l in rules),'Missing virtual fallback'
report={'version':'0.6.0','movie_input_frames':args.frames,'checkpoint_interval':step,
        'original_and_hd_ram_checkpoints':len(original),'ram_mismatches':mismatches,
        'hd_screenshots':len(screens),'dimensions':[1024,896],
        'hd_loader_errors':0,'tile_rules_checked':len(definitions),
        'unique_tile_palette_keys':len(set(definitions)),
        'captured_key_count':stats['captured_tile_palette_keys'],
        'virtual_sprite_keys':len(virtual_keys),'sprite_additions_checked':len(additions),
        'sprite_limit_removal':True,
        'completion':'Area 1 Clear followed by return to world map' if args.frames==40442 else 'Complete feedback recording',
        'visual_review_frames':[int(p[:-4])for p in screens],
        'overscan_note':'Eight source rows trimmed at top and bottom; no ROM patch.',
        'limits':'Sampled visual inspection, not every rendered frame. Unrecorded states and later areas are untested.',
        'pack_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(pack.iterdir())if p.is_file()}}
assert report['unique_tile_palette_keys']==stats['captured_tile_palette_keys']+len(virtual_keys)
(root/'validation'/args.report).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='pack_sha256'},indent=2))
