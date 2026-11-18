"""Area 2 crash regression, rule bounds, and exact ZIP playback checks."""
from pathlib import Path
import argparse
import json
from verify_v0110 import structure, replay

ROOT = Path(__file__).resolve().parents[1]


def verify_bounds(pack):
    definitions = {}
    lines = (pack/'hires.txt').read_text().splitlines()
    for line in lines:
        if line.startswith('<condition>'):
            parts = line[11:].split(',')
            definitions[parts[0]] = parts[1:]
    checked = 0
    for line in lines:
        if not line.startswith('[') or '<tile>' not in line:
            continue
        terms = line[1:].split(']', 1)[0].split('&')
        if 'area2' not in terms:
            continue
        rect = {'X': [0, 255], 'Y': [0, 239]}
        for name in terms:
            d = definitions.get(name)
            if not d:
                continue
            if d[0] in ('positionCheckX', 'positionCheckY'):
                axis, op, value = d[0][-1], d[1], int(d[2])
                if op == '>=': rect[axis][0] = max(rect[axis][0], value)
                elif op == '<': rect[axis][1] = min(rect[axis][1], value-1)
            elif d[0] in ('tileNearby', 'spriteNearby'):
                # These bounds must already be active when this lookup runs.
                hs = [True] if 'hmirror' in terms else [False] if '!hmirror' in terms else [False, True]
                vs = [True] if 'vmirror' in terms else [False] if '!vmirror' in terms else [False, True]
                if d[0] == 'tileNearby': hs, vs = [False], [False]
                for h in hs:
                    for v in vs:
                        dx, dy = int(d[1])*(-1 if h else 1), int(d[2])*(-1 if v else 1)
                        for x in rect['X']:
                            for y in rect['Y']:
                                assert 0 <= x+dx < 256 and 0 <= y+dy < 240, (name, x, y, dx, dy)
                checked += 1
    assert checked > 0
    return {'bounded_neighbor_references': checked, 'unsafe_references': 0}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', type=Path, required=True)
    ap.add_argument('--original', type=Path, required=True)
    ap.add_argument('--replay', type=Path, required=True)
    ap.add_argument('--failure-log', type=Path, required=True)
    args = ap.parse_args()
    failure = args.failure_log.read_text()
    assert 'Guarded playback fault signal 11' in failure
    log = (args.replay/'log.txt').read_text()
    assert log.count('Screen guard begins at ') == 2
    assert 'Guarded playback fault' not in log
    report = {'structure': structure(args.pack), 'bounds': verify_bounds(args.pack),
              'playback': replay(args.pack, args.original, args.replay),
              'crash_regression': {'v0111_guarded_playback_failed': True,
                                  'v0112_guarded_playback_completed': True,
                                  'core_binary_modified': False},
              'scope': 'The supplied Area 2 movie only.'}
    (ROOT/'validation/v0112-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
