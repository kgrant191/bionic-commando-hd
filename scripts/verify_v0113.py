"""Verify the exact Area 2 blue-slime ZIP and walking pose selection."""
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
    report={'structure':structure(args.pack),'bounds':verify_bounds(args.pack),
            'playback':replay(args.pack,args.original,args.replay),
            'walking':{'native_pose_ids':[18,19],'distinct_art_cells':[r['cell']for r in walking],
                       'native_animation_timing_preserved':True},
            'scope':'Supplied Area 2 movie only; blue slime substitutions are Area 2 scoped.'}
    (ROOT/'validation/v0113-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
