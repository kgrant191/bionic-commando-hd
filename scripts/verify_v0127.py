"""Verify tree selection/contours and preserve the approved Area 3 playback."""
from pathlib import Path
from collections import Counter
import argparse, csv, json
from PIL import Image
from verify_v0120 import scope, bounds, replay
from verify_v0110 import structure
from verify_v0122 import selected_art
from verify_v0126 import terrain_selection, warning_timing

ROOT = Path(__file__).resolve().parents[1]


def tree_selection(pack, baseline, result):
    build = json.loads((ROOT/'validation/v0127-build.json').read_text())
    pairs = {(k, int(p, 16)) for k, p in build['changed_pairs']}
    def source(directory):
        lines = (directory/'hires.txt').read_text().splitlines()
        return ([s[5:] for s in lines if s.startswith('<img>')],
                [s for s in lines if '<tile>' in s])
    images, tiles = source(pack)
    old_images, old_tiles = source(baseline)
    atlas = images.index('area3-trees-v0127.png')
    observed = set()
    for r in csv.DictReader((result/'home/audit.tsv').open(), delimiter='\t'):
        pair = r['key'], int(r['palette'], 16)
        if pair not in pairs: continue
        assert int(tiles[int(r['rule'])].split('<tile>')[1].split(',')[0]) == atlas, r
        observed.add(pair)
    assert observed == pairs
    def alpha(directory, names, rows, pair):
        for line in rows:
            a = line.split('<tile>')[1].split(',')
            if (a[1], int(a[2], 16)) != pair: continue
            x, y = int(a[3]), int(a[4])
            return Image.open(directory/names[int(a[0])]).convert('RGBA').crop((x,y,x+32,y+32)).getchannel('A').tobytes()
        raise AssertionError(pair)
    for pair in pairs:
        assert alpha(pack, images, tiles, pair) == alpha(baseline, old_images, old_tiles, pair), pair
    return {'tree_patterns_verified': len(observed), 'native_alpha_contours_unchanged': len(pairs),
            'old_tree_art_fallbacks': 0}


def unchanged_art(pack, baseline, result, old_result):
    build = json.loads((ROOT/'validation/v0127-build.json').read_text())
    pairs = {(k, int(p, 16)) for k, p in build['changed_pairs']}
    def states(directory, source):
        rules = [s for s in (source/'hires.txt').read_text().splitlines() if '<tile>' in s]
        found = Counter()
        for r in csv.DictReader((directory/'home/audit.tsv').open(), delimiter='\t'):
            if (r['key'], int(r['palette'], 16)) in pairs: continue
            assert int(r['rule']) >= 0
            found[tuple(v for k, v in r.items() if k != 'rule')+(rules[int(r['rule'])],)] += 1
        return found
    before, after = states(old_result, baseline), states(result, pack)
    assert before == after, {'missing': len(before-after), 'added': len(after-before)}
    compared = 0
    for p in (old_result/'frames').glob('*.png'):
        # Native tree visibility is 1062..1963; include the callback offset.
        if 1060 <= int(p.stem) <= 1970 or not p.stat().st_size: continue
        q = result/'frames'/p.name
        if q.exists():
            assert p.read_bytes() == q.read_bytes(), p.name
            compared += 1
    assert compared > 800
    return {'unchanged_other_graphics_states': sum(before.values()),
            'unchanged_screenshots_outside_tree_sequence': compared,
            'changed_tree_pairs': len(pairs)}


def main():
    parser = argparse.ArgumentParser()
    for arg in ['pack', 'baseline', 'boss-baseline', 'original', 'replay', 'baseline-replay']:
        parser.add_argument('--'+arg, type=Path, required=True)
    a = parser.parse_args()
    terrain = json.loads((ROOT/'validation/v0126-build.json').read_text())
    materials = {k: 'area3-readability-v0126.png' for k in terrain['passable_snow_keys']}
    materials.update({k: 'area3-classic-v0125.png' for k in terrain['preserved_solid_stone_keys']})
    report = {'scope': scope(a.pack, a.baseline), 'structure': structure(a.pack),
              'bounds': bounds(a.pack), 'playback': replay(a.pack, a.original, a.replay),
              'trees': tree_selection(a.pack, a.baseline, a.replay),
              'selected_art': selected_art(a.pack, a.boss_baseline, a.replay, materials),
              'unchanged_art': unchanged_art(a.pack, a.baseline, a.replay, a.baseline_replay),
              'terrain_selection': terrain_selection(a.pack, a.replay),
              'warning_timing': warning_timing(a.replay, a.baseline_replay)}
    captures = list((a.replay/'frames').glob('*.png'))
    valid = [p for p in captures if p.stat().st_size]
    for p in valid:
        with Image.open(p) as im: im.verify()
    report['playback']['screenshots'] = len(valid)
    report['playback']['empty_startup_captures'] = len(captures)-len(valid)
    (ROOT/'validation/v0127-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
