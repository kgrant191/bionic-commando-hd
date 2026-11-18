"""Check the unified snowy cliff and the exact-ZIP Area 3 replay."""
from pathlib import Path
from collections import Counter
import argparse, csv, json
from PIL import Image
from verify_v0120 import scope, bounds, replay
from verify_v0110 import structure
from verify_v0122 import selected_art

ROOT = Path(__file__).resolve().parents[1]


def snow_selection(pack, result):
    lines = (pack/'hires.txt').read_text().splitlines()
    images = [s[5:] for s in lines if s.startswith('<img>')]
    tiles = [s for s in lines if '<tile>' in s]
    atlas = images.index('area3-snowface-v0124.png')
    door_atlas = images.index('area3-surfaces-v0122.png')
    parts = json.loads((ROOT/'capture/area3/door-v0122.json').read_text())
    door_pairs = {(p[2], p[3]) for p in parts}
    build = json.loads((ROOT/'validation/v0124-build.json').read_text())
    pairs = {(k, int(p, 16)) for k,p in build['changed_pairs']}
    observed, snowy, doorway = set(), 0, 0
    for r in csv.DictReader((result/'home/audit.tsv').open(), delimiter='\t'):
        pair = r['key'], int(r['palette'], 16)
        if pair not in pairs: continue
        im = int(tiles[int(r['rule'])].split('<tile>')[1].split(',')[0])
        observed.add(pair)
        if im == atlas: snowy += 1
        else:
            assert im == door_atlas and pair in door_pairs, r
            doorway += 1
    assert observed == pairs, pairs-observed
    return {'material_pairs_verified': len(observed), 'snow_states': snowy,
            'retained_door_states': doorway, 'old_rock_or_vegetation_fallbacks': 0}


def unchanged_art(pack, baseline, result, old_result):
    build = json.loads((ROOT/'validation/v0124-build.json').read_text())
    pairs = {(k, int(p, 16)) for k,p in build['changed_pairs']}
    def states(directory, source):
        rules = [s for s in (source/'hires.txt').read_text().splitlines() if '<tile>' in s]
        found = Counter()
        for r in csv.DictReader((directory/'home/audit.tsv').open(), delimiter='\t'):
            if (r['key'], int(r['palette'], 16)) in pairs:
                continue
            assert int(r['rule']) >= 0
            found[tuple(v for k,v in r.items() if k != 'rule')+(rules[int(r['rule'])],)] += 1
        return found
    before, after = states(old_result, baseline), states(result, pack)
    assert before == after, {'missing': len(before-after), 'added': len(after-before)}
    compared = 0
    for p in (old_result/'frames').glob('*.png'):
        # Inclusive transition margin around outdoor terrain visibility.
        if 1040 <= int(p.stem) <= 5080 or not p.stat().st_size: continue
        q = result/'frames'/p.name
        if q.exists():
            assert p.read_bytes() == q.read_bytes(), p.name
            compared += 1
    assert compared > 200
    return {'unchanged_other_graphics_states': sum(before.values()),
            'unchanged_nonoutdoor_screenshots': compared,
            'changed_material_pairs': len(pairs)}


def main():
    parser = argparse.ArgumentParser()
    for arg in ['pack', 'baseline', 'boss-baseline', 'original', 'replay', 'baseline-replay']:
        parser.add_argument('--'+arg, type=Path, required=True)
    a = parser.parse_args()
    report = {'scope': scope(a.pack, a.baseline), 'structure': structure(a.pack),
              'bounds': bounds(a.pack), 'playback': replay(a.pack, a.original, a.replay),
              'selected_art': selected_art(a.pack, a.boss_baseline, a.replay, 'area3-snowface-v0124.png'),
              'unchanged_art': unchanged_art(a.pack, a.baseline, a.replay, a.baseline_replay),
              'snow_selection': snow_selection(a.pack, a.replay)}
    captures = list((a.replay/'frames').glob('*.png'))
    valid = [p for p in captures if p.stat().st_size]
    for p in valid:
        with Image.open(p) as im: im.verify()
    report['playback']['screenshots'] = len(valid)
    report['playback']['empty_startup_captures'] = len(captures)-len(valid)
    (ROOT/'validation/v0124-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
