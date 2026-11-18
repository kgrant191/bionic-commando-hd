"""Check solid/passable materials, native warning timing and Area 3 playback."""
from pathlib import Path
from collections import Counter
import argparse, csv, json
from PIL import Image
from verify_v0120 import scope, bounds, replay
from verify_v0110 import structure
from verify_v0122 import selected_art

ROOT = Path(__file__).resolve().parents[1]


def terrain_selection(pack, result):
    lines = (pack/'hires.txt').read_text().splitlines()
    images = [s[5:] for s in lines if s.startswith('<img>')]
    tiles = [s for s in lines if '<tile>' in s]
    atlas = images.index('area3-readability-v0126.png')
    build = json.loads((ROOT/'validation/v0126-build.json').read_text())
    pairs = {(k, int(p, 16)) for k,p in build['changed_pairs']}
    observed, terrain = set(), 0
    for r in csv.DictReader((result/'home/audit.tsv').open(), delimiter='\t'):
        pair = r['key'], int(r['palette'], 16)
        if pair not in pairs: continue
        im = int(tiles[int(r['rule'])].split('<tile>')[1].split(',')[0])
        observed.add(pair)
        assert im == atlas, r
        terrain += 1
    assert observed == pairs, pairs-observed
    solid = set(build['preserved_solid_stone_keys'])
    solid_rows = [r for r in csv.DictReader((result/'home/audit.tsv').open(), delimiter='\t')
                  if r['key'] in solid and int(r['palette'], 16) == 0x1C201000]
    assert {r['key'] for r in solid_rows} == solid
    previous = images.index('area3-classic-v0125.png')
    assert all(int(tiles[int(r['rule'])].split('<tile>')[1].split(',')[0]) == previous for r in solid_rows)
    return {'changed_pairs_verified': len(observed), 'changed_graphics_states': terrain,
            'passable_snow_patterns': len(build['passable_snow_keys']),
            'preserved_solid_stone_patterns': len(solid), 'previous_warning_fallbacks': 0}


def warning_timing(result, old_result):
    build = json.loads((ROOT/'validation/v0126-build.json').read_text())
    keys = {k for phase in build['warning_phases'] for k in phase}
    def summary(directory):
        found = {}
        for r in csv.DictReader((directory/'home/audit.tsv').open(), delimiter='\t'):
            if r['key'] not in keys or int(r['palette'], 16) != 0xFF30290F: continue
            first, last, count = int(r['first']), int(r['last']), int(r['instances'])
            a = found.setdefault(r['key'], {'first': first, 'last': last, 'instances': 0})
            a['first'] = min(a['first'], first); a['last'] = max(a['last'], last); a['instances'] += count
        return found
    before, after = summary(old_result), summary(result)
    assert set(after) == keys and before == after, (before, after)
    a = Image.open(ROOT/'validation/pose-previews/area3-warning-v0126/0.png').convert('RGBA')
    b = Image.open(ROOT/'validation/pose-previews/area3-warning-v0126/1.png').convert('RGBA')
    assert a.tobytes() != b.tobytes()
    native = json.loads((ROOT/'capture/area3/plant-warning-v0126.json').read_text())
    return {'distinct_painted_warning_phases': 2, 'native_warning_patterns': len(keys),
            'native_first_last_and_instance_counts_unchanged': True,
            'native_warning_frames': native['warning_frames'], 'sprite_instances': sum(v['instances'] for v in after.values()),
            'native_first_frame': min(v['first'] for v in after.values()),
            'native_last_frame': max(v['last'] for v in after.values())}


def unchanged_art(pack, baseline, result, old_result):
    build = json.loads((ROOT/'validation/v0126-build.json').read_text())
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
    build = json.loads((ROOT/'validation/v0126-build.json').read_text())
    gray_materials = {k: 'area3-readability-v0126.png' for k in build['passable_snow_keys']}
    gray_materials.update({k: 'area3-classic-v0125.png' for k in build['preserved_solid_stone_keys']})
    report = {'scope': scope(a.pack, a.baseline), 'structure': structure(a.pack),
              'bounds': bounds(a.pack), 'playback': replay(a.pack, a.original, a.replay),
              'selected_art': selected_art(a.pack, a.boss_baseline, a.replay, gray_materials),
              'unchanged_art': unchanged_art(a.pack, a.baseline, a.replay, a.baseline_replay),
              'terrain_selection': terrain_selection(a.pack, a.replay),
              'warning_timing': warning_timing(a.replay, a.baseline_replay)}
    captures = list((a.replay/'frames').glob('*.png'))
    valid = [p for p in captures if p.stat().st_size]
    for p in valid:
        with Image.open(p) as im: im.verify()
    report['playback']['screenshots'] = len(valid)
    report['playback']['empty_startup_captures'] = len(captures)-len(valid)
    (ROOT/'validation/v0126-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
