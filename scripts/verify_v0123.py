"""Check vegetation selection, unchanged other art and exact-ZIP Area 3 replay."""
from pathlib import Path
from collections import Counter
import argparse, csv, json
from PIL import Image
from verify_v0120 import scope, bounds, replay
from verify_v0110 import structure
from verify_v0122 import selected_art

ROOT = Path(__file__).resolve().parents[1]


def unchanged_art(pack, baseline, result, old_result):
    layout = json.loads((ROOT/'capture/area3/vegetation-layout-v0123.json').read_text())
    keys = set(layout['positions'])
    def states(directory, source):
        rules = [s for s in (source/'hires.txt').read_text().splitlines() if '<tile>' in s]
        found = Counter()
        for r in csv.DictReader((directory/'home/audit.tsv').open(), delimiter='\t'):
            if r['layer'] == '0' and int(r['palette'], 16) == 0x1C201000 and r['key'] in keys:
                continue
            assert int(r['rule']) >= 0
            found[tuple(v for k,v in r.items() if k != 'rule')+(rules[int(r['rule'])],)] += 1
        return found
    before, after = states(old_result, baseline), states(result, pack)
    assert before == after, {'missing': len(before-after), 'added': len(after-before)}
    compared = 0
    for p in (old_result/'frames').glob('*.png'):
        # Inclusive transition margin around outdoor vegetation visibility.
        if 1840 <= int(p.stem) <= 5080 or not p.stat().st_size: continue
        q = result/'frames'/p.name
        if q.exists():
            assert p.read_bytes() == q.read_bytes(), p.name
            compared += 1
    assert compared > 200
    return {'unchanged_other_graphics_states': sum(before.values()),
            'unchanged_nonoutdoor_screenshots': compared,
            'recorded_adjacencies_verified': layout['unique_adjacencies'],
            'layout_reference_frames': layout['recorded_frames_checked']}


def main():
    parser = argparse.ArgumentParser()
    for arg in ['pack', 'baseline', 'boss-baseline', 'original', 'replay', 'baseline-replay']:
        parser.add_argument('--'+arg, type=Path, required=True)
    a = parser.parse_args()
    report = {'scope': scope(a.pack, a.baseline), 'structure': structure(a.pack),
              'bounds': bounds(a.pack), 'playback': replay(a.pack, a.original, a.replay),
              'selected_art': selected_art(a.pack, a.boss_baseline, a.replay, 'area3-vegetation-v0123.png'),
              'unchanged_art': unchanged_art(a.pack, a.baseline, a.replay, a.baseline_replay)}
    captures = list((a.replay/'frames').glob('*.png'))
    valid = [p for p in captures if p.stat().st_size]
    for p in valid:
        with Image.open(p) as im: im.verify()
    report['playback']['screenshots'] = len(valid)
    report['playback']['empty_startup_captures'] = len(captures)-len(valid)
    (ROOT/'validation/v0123-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
