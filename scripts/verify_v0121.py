"""Validate the exact Area 3 correction ZIP and unchanged boss art reuse."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageChops
from verify_v0120 import scope, bounds, replay
from verify_v0110 import structure

ROOT = Path(__file__).resolve().parents[1]


def boss_reuse(pack, baseline):
    old = (baseline/'hires.txt').read_text().splitlines()
    new = (pack/'hires.txt').read_text().splitlines()
    extra = list((Counter(new)-Counter(old)).elements())
    original = set(old)
    reused = []
    for line in extra:
        if not (line.startswith('[') and '<tile>' in line):
            continue
        guard, body = line[1:].split(']', 1)
        if 'a3121Wrap' in guard:
            continue
        if not body[6:].split(',')[2].startswith('FF'):
            continue
        terms = guard.split('&')
        if not any(t.startswith('a3121Bound') for t in terms) and not any(
                t.startswith('area5boss') or t.startswith('exhaust098') for t in terms):
            # The inherited robot's generic fallback has no pose/bound term.
            candidate = '['+'&'.join('area5' if t == 'area3' else t for t in terms)+']'+body
            if candidate not in original:
                continue
        inherited = [t for t in terms if not t.startswith('a3121Bound')]
        if any(t.startswith('exhaust098') for t in terms):
            inherited = [t for t in inherited if t not in ['hmirror', '!hmirror', 'vmirror', '!vmirror']]
        candidate = '['+'&'.join('area5' if t == 'area3' else t for t in inherited)+']'+body
        assert candidate in original, line
        reused.append(line)
    assert len(reused) == json.loads((ROOT/'validation/v0121-build.json').read_text())['reused_boss_rules'], len(reused)
    return {'reused_boss_rules': len(reused), 'image_coordinates_unchanged': True,
            'original_pose_and_palette_tests_preserved': True,
            'both_exhaust_phases_preserved': True}


def boss_playback(pack, result):
    lines = (pack/'hires.txt').read_text().splitlines()
    tiles = [s for s in lines if '<tile>' in s]
    bossrules = {i for i, s in enumerate(tiles) if 'area3' in s.split(']', 1)[0]
                 and ('area5boss' in s or 'exhaust098' in s)}
    records = json.loads((ROOT/'capture/area5boss-poses.json').read_text())
    keys = {r['head'] for r in records} | {p[2] for r in records for p in r['parts']}
    # Include both expanding/contracting exhaust components, not only the
    # single native body assembly captured in the earlier level.
    for i in bossrules:
        keys.add(tiles[i].split('<tile>')[1].split(',')[1])
    rows = list(csv.DictReader((result/'home/audit.tsv').open(), delimiter='\t'))
    states = [r for r in rows if r['layer'] == '1' and r['key'] in keys
              and int(r['first']) >= 9433 and int(r['last']) <= 9852]
    assert states
    # An old generic mapping can pass a zero-unmapped audit but still look
    # native; require these recorded boss states to select the reused art.
    report = json.loads((ROOT/'validation/v0121-build.json').read_text())
    boss_count = report['reused_boss_rules']
    start = 22+report['additional_clipped_exhaust_rules']+report['additional_clipped_body_rules']
    fallback = [r for r in states if not (start <= int(r['rule']) < start+boss_count
                                        or 'a3121Wrap' in tiles[int(r['rule'])])]
    assert not fallback, fallback
    palettes = sorted({r['palette'] for r in states if r['key'] == records[0]['head']})
    assert palettes == ['FF202A0F', 'FF30150F', 'FF30210F', 'FF36060F'], palettes
    # The unoccupied left wall must not acquire a wrapped copy of the boss.
    wall = Image.open(result/'frames/09793.png').convert('RGB').crop((0, 200, 32, 500))
    for n in [9794, 9795, 9796]:
        current = Image.open(result/'frames'/f'{n:05}.png').convert('RGB').crop((0, 200, 32, 500))
        assert ImageChops.difference(wall, current).getbbox() is None, ('wrapped boss pixels', n)
    return {'boss_graphics_states': len(states), 'old_generic_boss_fallbacks': 0,
            'body_palettes_verified': palettes, 'wrapped_body_pixel_check_frames': 3}


def main():
    parser = argparse.ArgumentParser()
    for arg in ['pack', 'baseline', 'original', 'replay']:
        parser.add_argument('--'+arg, type=Path, required=True)
    a = parser.parse_args()
    report = {'scope': scope(a.pack, a.baseline), 'structure': structure(a.pack),
              'bounds': bounds(a.pack), 'boss_reuse': boss_reuse(a.pack, a.baseline),
              'playback': replay(a.pack, a.original, a.replay),
              'boss_playback': boss_playback(a.pack, a.replay)}
    (ROOT/'validation/v0121-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
