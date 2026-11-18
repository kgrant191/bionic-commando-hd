"""Check the eagle-only change and exact extracted-ZIP Area 2 playback."""
from collections import Counter
from pathlib import Path
import argparse
import json
from build_v0115 import EAGLE_KEYS, NORMAL
from verify_v0110 import structure, replay
from verify_v0112 import verify_bounds

ROOT = Path(__file__).resolve().parents[1]


def scope(pack, baseline):
    old = (baseline/'hires.txt').read_text().splitlines()
    new = (pack/'hires.txt').read_text().splitlines()
    images = [s[5:] for s in new if s.startswith('<img>')]
    index = str(images.index('boss-door-eagle-v0115.png'))
    rules = [s for s in new if '<tile>' in s and s.split('<tile>')[1].split(',')[0] == index]
    before = Counter(s for s in old if '<tile>' in s)
    after = Counter(s for s in new if '<tile>' in s) - Counter(rules)
    assert before == after, 'An existing non-emblem rule changed'
    unchanged = 0
    for path in baseline.glob('*.png'):
        assert path.read_bytes() == (pack/path.name).read_bytes(), path.name
        unchanged += 1
    wanted = {(s.split('<tile>')[1].split(',')[1], s.split('<tile>')[1].split(',')[2])
              for s in old if '<tile>' in s and s.split('<tile>')[1].split(',')[1] in EAGLE_KEYS
              and s.split('<tile>')[1].split(',')[2].startswith('0F')}
    actual = set()
    for line in rules:
        guard, body = line.split('<tile>')
        assert guard == '['+NORMAL+']'
        fields = body.split(',')
        assert fields[1] in EAGLE_KEYS and fields[2].startswith('0F')
        actual.add((fields[1], fields[2]))
        first = next(s for s in new if '<tile>' in s and s.split('<tile>')[1].split(',')[1:3] == fields[1:3])
        assert first == line, 'Emblem must precede the ordinary painted header'
    assert actual == wanted
    return {'new_emblem_rules': len(rules), 'covered_native_palette_pairs': len(actual),
            'existing_pngs_unchanged': unchanged, 'existing_tile_rules_unchanged': sum(before.values()),
            'radio_and_ordinary_door_patterns_changed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ['pack', 'baseline', 'original', 'replay']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    log = (args.replay/'log.txt').read_text()
    assert log.count('Screen guard begins at ') == 2 and 'Guarded playback fault' not in log
    report = {'scope': scope(args.pack, args.baseline), 'structure': structure(args.pack),
              'bounds': verify_bounds(args.pack), 'playback': replay(args.pack, args.original, args.replay)}
    (ROOT/'validation/v0115-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
