"""Verify Area 3 surface/door/blast selection and the full exact-ZIP replay."""
from pathlib import Path
import argparse, csv, json
from PIL import Image, ImageChops
from verify_v0120 import scope, bounds, replay
from verify_v0110 import structure

ROOT = Path(__file__).resolve().parents[1]


def selected_art(pack, baseline, result, recess_image='area3-surfaces-v0122.png'):
    lines = (pack/'hires.txt').read_text().splitlines()
    images = [s[5:] for s in lines if s.startswith('<img>')]
    tiles = [s for s in lines if '<tile>' in s]
    atlas = images.index('area3-surfaces-v0122.png')
    recess_atlas = images.index(recess_image)
    rows = list(csv.DictReader((result/'home/audit.tsv').open(), delimiter='\t'))
    report = json.loads((ROOT/'validation/v0122-build.json').read_text())
    def image_id(r): return int(tiles[int(r['rule'])].split('<tile>')[1].split(',')[0])
    recess = [r for r in rows if r['layer'] == '0' and int(r['palette'], 16) == 0x1C201000 and r['key'] in report['recess_keys']]
    assert {r['key'] for r in recess} == set(report['recess_keys'])
    assert all(image_id(r) == recess_atlas for r in recess)
    blasts = [r for r in rows if r['layer'] == '1' and r['key'] in report['explosion_keys']]
    assert {r['key'] for r in blasts} == set(report['explosion_keys'])
    assert all(image_id(r) == atlas for r in blasts), blasts
    assert min(int(r['first']) for r in blasts) == 9852
    assert max(int(r['last']) for r in blasts) == 9867
    parts = json.loads((ROOT/'capture/area3/door-v0122.json').read_text())
    doorpairs = {(p[2], p[3]) for p in parts}
    doors = [r for r in rows if r['layer'] == '0' and (r['key'], int(r['palette'], 16)) in doorpairs and image_id(r) == atlas]
    assert len({r['rule'] for r in doors}) == 16
    # Body/exhaust fixes remain selected from exactly the approved baseline
    # rules; the destruction family is tested independently above.
    old = [s for s in (baseline/'hires.txt').read_text().splitlines() if '<tile>' in s]
    old_report = json.loads((ROOT/'validation/v0121-build.json').read_text())
    start = 22+old_report['additional_clipped_exhaust_rules']+old_report['additional_clipped_body_rules']
    approved = set(old[start:start+old_report['reused_boss_rules']]) | {s for s in old if 'a3121Wrap' in s}
    keys = {s.split('<tile>')[1].split(',')[1] for s in approved}
    boss = [r for r in rows if r['layer'] == '1' and r['key'] in keys and int(r['first']) >= 9433 and int(r['last']) <= 9851]
    assert boss and all(tiles[int(r['rule'])] in approved for r in boss)
    wall = Image.open(result/'frames/09793.png').convert('RGB').crop((0, 200, 32, 500))
    for n in [9794, 9795, 9796]:
        current = Image.open(result/'frames'/f'{n:05}.png').convert('RGB').crop((0, 200, 32, 500))
        assert ImageChops.difference(wall, current).getbbox() is None, n
    return {'recess_patterns_verified': len({r['key'] for r in recess}),
            'door_cells_verified': 16, 'explosion_patterns_verified': len(report['explosion_keys']),
            'explosion_states_verified': len(blasts), 'explosion_frames': 16,
            'old_explosion_fallbacks': 0, 'retained_boss_states': len(boss),
            'wrapped_body_pixel_check_frames': 3}


def main():
    parser = argparse.ArgumentParser()
    for arg in ['pack', 'baseline', 'original', 'replay']: parser.add_argument('--'+arg, type=Path, required=True)
    a = parser.parse_args()
    report = {'scope': scope(a.pack, a.baseline), 'structure': structure(a.pack),
              'bounds': bounds(a.pack), 'playback': replay(a.pack, a.original, a.replay),
              'selected_art': selected_art(a.pack, a.baseline, a.replay)}
    # The core has not produced an image when the frame-one callback runs.
    # Count actual PNG captures, and retain the empty startup capture count.
    captures = list((a.replay/'frames').glob('*.png'))
    valid = [p for p in captures if p.stat().st_size]
    for p in valid:
        with Image.open(p) as im: im.verify()
    report['playback']['screenshots'] = len(valid)
    report['playback']['empty_startup_captures'] = len(captures)-len(valid)
    (ROOT/'validation/v0122-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
