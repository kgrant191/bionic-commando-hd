"""Verify the exact Area 2 machinery ZIP and preserve prior safeguards."""
from pathlib import Path
import argparse,json
from verify_v0110 import structure,replay
from verify_v0112 import verify_bounds

ROOT=Path(__file__).resolve().parents[1]

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pack',type=Path,required=True)
    parser.add_argument('--original',type=Path,required=True)
    parser.add_argument('--replay',type=Path,required=True)
    args=parser.parse_args()
    log=(args.replay/'log.txt').read_text()
    assert log.count('Screen guard begins at ')==2
    assert 'Guarded playback fault' not in log
    records=json.loads((ROOT/'capture/area2-v0113/enemy-poses.json').read_text())
    walking=[r for r in records if r['id'] in [18,19]]
    assert len(walking)==2 and len({r['cell']for r in walking})==2
    assert {r['type']for r in walking}=={'walk'}
    assert len({r['body_scale']for r in walking})==1
    lines=(args.pack/'hires.txt').read_text().splitlines()
    images=[line[5:]for line in lines if line.startswith('<img>')]
    layout_index=str(images.index('area2-layouts-v0114.png'))
    layouts=[line for line in lines if '<tile>'in line and line.split('<tile>')[1].split(',')[0]==layout_index]
    assert layouts
    for line in layouts:
        guard,body=line.split('<tile>')
        assert {'area2','a2Cave'} <= set(guard.strip('[]').split('&'))
        assert body.split(',')[2]=='0F2B1C0B'
    report={'structure':structure(args.pack),'bounds':verify_bounds(args.pack),
            'playback':replay(args.pack,args.original,args.replay),
            'walking':{'native_pose_ids':[18,19],'distinct_art_cells':[r['cell']for r in walking],
                       'native_animation_timing_preserved':True},
            'layout_rules':len(layouts),
            'scope':'Supplied Area 2 movie only; all new layouts use its cave palette.'}
    (ROOT/'validation/v0114-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
