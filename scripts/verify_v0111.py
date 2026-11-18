"""Reuse structural/state checks, with a separate report for the Area 2 revision."""
from pathlib import Path
import argparse,json
from verify_v0110 import structure,replay

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--pack',type=Path,default=ROOT/'pack')
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--replay',type=Path,required=True)
    args=ap.parse_args()
    report={'structure':structure(args.pack),'playback':replay(args.pack,args.original,args.replay),
            'scope':'Area 2 only; no previous-area recordings replayed in this revision.',
            'visual_quality':'Assessed separately through screenshot and motion-sequence review; rule coverage alone is not a visual-quality test.'}
    (ROOT/'validation/v0111-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
