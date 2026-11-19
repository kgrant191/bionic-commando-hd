"""Check the installed doorway package against the Area 8 movie and its PPU tile captures."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from build_v0153 import COPPER, DATA, EMPTY, STEEL, door_art, faded
from verify_v0110 import structure
from verify_v0151 import digest, same_state


def geometry(layouts):
    origins=defaultdict(set)
    for layout in layouts.values():
        for y,row in enumerate(layout):
            for x,key in enumerate(row):
                if key != EMPTY:
                    origins[key].add((x,y))
    return origins


def confined_changes(tiles, before, after, layouts, art):
    origins=geometry(layouts)
    palettes={faded(p,l) for p in (*STEEL,*COPPER) for l in (0,1,2)}
    compared=changed=boundary_checks=0
    for tilefile in sorted(tiles.glob('*.tiles')):
        n=tilefile.stem
        left=before/'frames'/f'{n}.png';right=after/'frames'/f'{n}.png'
        if not left.is_file() or not right.is_file():continue
        compared+=1
        if digest(left)==digest(right):continue
        with Image.open(left) as a,Image.open(right) as b:
            delta=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
        if delta.getbbox() is None:continue
        changed+=1
        door_bounds=set()
        for line in tilefile.read_text().splitlines():
            if not line.startswith('0,'):continue
            _,x,y,key,color,_,_=line.split(',')
            if color not in palettes:continue
            for dx,dy in origins.get(key,()):
                door_bounds.add((int(x)-dx*8, int(y)-dy*8-8))
        draw=ImageDraw.Draw(delta)
        for x,y in door_bounds:
            draw.rectangle((x*4,(y*4),4*(x+32)-1,4*(y+32)-1),fill=(0,0,0))
        box=delta.getbbox()
        if box:
            # The source trace samples every second native column. A door that
            # starts at column 255 can show exactly one column before entering
            # the trace. Verify those displayed pixels against the door itself.
            assert box[0]>=1020 and box[2]<=1024, ('changed outside the door',n,box)
            active=np.asarray(delta).any(axis=(1,2))
            ys=np.flatnonzero(active)
            with Image.open(right) as rendered:
                for group in np.split(ys,np.where(np.diff(ys)>1)[0]+1):
                    top,bottom=int(group[0]),int(group[-1])+1
                    strip=np.asarray(rendered.crop((1020,top,1024,bottom)).convert('RGB'))
                    height=bottom-top
                    assert any(np.array_equal(strip,template[start:start+height,:4]) for template in art
                               for start in range(top%4,129-height,4)), ('unrecognized edge drawing',n,box)
                    boundary_checks+=1
    assert compared>=1000 and changed>100
    return compared,changed,boundary_checks


def trace(path):
    return {int(line.split()[0]) for line in path.read_text().splitlines() if line}


def screenshot_state(before,after):
    if not (after/'continuation.json').exists():
        same_state(before,after,frames=24505)
        return 1
    # A screenshot capture may stop at its wall-clock limit while the direct
    # full-movie renderer finishes. Validate both capture segments and overlap.
    record=json.loads((after/'continuation.json').read_text())
    tail=Path(record['capture']);start=record['start_frame'];end=24505
    assert int((tail/'home/done').read_text())==end-start
    for name,width in [('ram.bin',2048),('oam.bin',256),('palette.bin',32)]:
        full=(before/name).read_bytes()
        head=(after/name).read_bytes()
        assert len(head)%width==0 and len(head)>start*width
        assert head==full[:len(head)] and (tail/name).read_bytes()==full[start*width:end*width]
    checked_overlap=0
    for n in range(start+1,end+1):
        if n%24 and n!=end:continue
        short=tail/'frames'/f'{n-start:05}.png'
        assert short.read_bytes()==(after/'frames'/f'{n:05}.png').read_bytes()
        checked_overlap+=int(n<=record['last_prefix_frame'])
    assert checked_overlap>=20
    return 2


def verify(before,after,old_scan,new_scan,tiles,pack,previous_pack,archive):
    same_state(before,old_scan,new_scan,frames=24505)
    segments=screenshot_state(before,after)
    old_frames=trace(old_scan/'headers.tsv')
    new_frames=trace(new_scan/'headers.tsv')
    assert len(old_frames)>1000 and not new_frames, (len(old_frames),len(new_frames))
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert {Path(f).name for f in z.namelist()} == {p.name for p in pack.iterdir()}
        for f in z.namelist():assert z.read(f)==(pack/Path(f).name).read_bytes()
    sizes={f.name:(1152,1104) for f in pack.glob('area8-recoil-*-v0152.png')}
    stats=structure(pack,sizes)
    cfg=json.loads((DATA/'doors-v0153.json').read_text())
    layouts=cfg['layouts']
    art=door_art(previous_pack,(previous_pack/'hires.txt').read_text().splitlines(),layouts)
    tests=[*cfg['examples'],dict(frame=17496,x=96,y=30,kind='radio',palette='0F271606')]
    targets=[]
    for ex in tests:
        n,x,y,kind,col=(ex[k]for k in ('frame','x','y','kind','palette'))
        coords=(4*x,4*(y-8),4*x+128,4*(y-8)+128)
        png=f'{n:05}.png'
        with Image.open(after/'frames'/png) as new, Image.open(before/'frames'/png) as old:
            target=np.asarray(art['copper' if col in COPPER else 'steel',kind].convert('RGB'))
            newscore=float((np.asarray(new.crop(coords).convert('RGB'))==target).all(axis=2).mean())
            oldscore=float((np.asarray(old.crop(coords).convert('RGB'))==target).all(axis=2).mean())
        assert newscore>.98,(n,oldscore,newscore)
        if kind=='goal':assert oldscore==newscore,(n,oldscore,newscore)
        else:assert newscore-oldscore>.3,(n,oldscore,newscore)
        targets.append(dict(frame=n,kind=kind,prior=round(oldscore,4),current=round(newscore,4)))
    templates=[np.asarray(im.convert('RGB')) for im in art.values()]
    compared,changed,boundary=confined_changes(tiles,before,after,layouts,templates)
    return dict(recording_frames=24505,matching_game_state_frames=24505,screenshot_capture_segments=segments,
                previous_frames_with_old_headers=len(old_frames),new_frames_with_old_headers=len(new_frames),
                compared_tile_capture_frames=compared,visually_changed_frames_among_samples=changed,
                sampled_changes_outside_doors=0,edge_strips_verified_against_art=boundary,doorway_art_matches=targets,
                structure=stats,archive_sha256=digest(archive))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('before','after','old_scan','new_scan','tiles','pack','previous_pack','archive'):
        parser.add_argument(name,type=Path)
    print(json.dumps(verify(**vars(parser.parse_args())),indent=2))
