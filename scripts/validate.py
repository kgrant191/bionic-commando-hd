"""Check installed-pack structure and deterministic original/HD movie parity."""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('--original',type=Path,required=True)
parser.add_argument('--hd',type=Path,required=True)
parser.add_argument('--home',type=Path,required=True)
parser.add_argument('--log',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];pack=root/'pack'
rules=(pack/'hires.txt').read_text().splitlines()
images=[];definitions=[]
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
assert '<overscan>8,0,8,0' in rules
stop_marker=int((args.home/'done').read_text())
assert 40442<=stop_marker<=40444 # The older capture script can tick once after a pause request.
assert (args.hd/'40442.ram').is_file()
original=list(sorted(args.original.glob('*.ram')))
assert len(original)==339, len(original)
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
report={'version':'0.1.0','movie_input_frames':40442,
        'original_and_hd_ram_checkpoints':len(original),'ram_mismatches':mismatches,
        'hd_screenshots':len(screens),'dimensions':[1024,896],
        'hd_loader_errors':0,'tile_rules_checked':len(definitions),
        'unique_tile_palette_keys':len(set(definitions)),
        'captured_key_count':stats['captured_tile_palette_keys'],
        'completion':'Area 1 Clear followed by return to world map',
        'visual_review_frames':[480,1200,1920,3000,3480,3960,7320,11640,21720,38400,39360,39840,40442],
        'overscan_note':'Eight source rows trimmed at top and bottom; no ROM patch.',
        'limits':'Sampled visual inspection, not every rendered frame. Unrecorded states and later areas are untested.',
        'pack_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(pack.iterdir())if p.is_file()}}
assert report['unique_tile_palette_keys']==stats['captured_tile_palette_keys']
(root/'validation/replay.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='pack_sha256'},indent=2))
