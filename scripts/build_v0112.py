"""Opaque Area 2 doorway and screen-bounded native-neighbor lookups."""
from pathlib import Path
import argparse
import json
from build_v0111 import build as previous_build

ROOT = Path(__file__).resolve().parents[1]


def guard_area2_neighbors(lines):
    """Short-circuit before Mesen's one-past-the-screen nearby lookup bug.

    Keep every earlier-area rule untouched. Both axes are bounded to prevent
    horizontal row wrapping as well as the known ScreenPixelCount overread.
    """
    nearby = {}
    for line in lines:
        if line.startswith('<condition>'):
            fields = line[11:].split(',')
            if fields[1] in ('tileNearby', 'spriteNearby'):
                nearby[fields[0]] = (fields[1], int(fields[2]), int(fields[3]))
    positions = {}
    declarations = []

    def position(axis, op, value):
        key = axis, op, value
        if key not in positions:
            name = f'a212Bound{len(positions)}'
            positions[key] = name
            declarations.append(f'<condition>{name},positionCheck{axis},{op},{value}')
        return positions[key]

    result = []
    guarded = 0
    for line in lines:
        if not (line.startswith('[') and '<tile>' in line):
            result.append(line)
            continue
        guard, body = line[1:].split(']', 1)
        terms = guard.split('&')
        if 'area2' not in terms:
            result.append(line)
            continue
        xmin, xmax, ymin, ymax = 0, 256, 0, 240
        found = False
        for name in terms:
            assert not (name.startswith('!') and name[1:] in nearby), name
            if name not in nearby:
                continue
            found = True
            kind, dx, dy = nearby[name]
            xs, ys = [dx], [dy]
            if kind == 'spriteNearby':
                xs = [-dx] if 'hmirror' in terms else [dx] if '!hmirror' in terms else [-abs(dx), abs(dx)]
                ys = [-dy] if 'vmirror' in terms else [dy] if '!vmirror' in terms else [-abs(dy), abs(dy)]
            xmin = max(xmin, *(-x for x in xs))
            xmax = min(xmax, *(256-x for x in xs))
            ymin = max(ymin, *(-y for y in ys))
            ymax = min(ymax, *(240-y for y in ys))
        if not found:
            result.append(line)
            continue
        checks = []
        if xmin > 0: checks.append(position('X', '>=', xmin))
        if xmax < 256: checks.append(position('X', '<', xmax))
        if ymin > 0: checks.append(position('Y', '>=', ymin))
        if ymax < 240: checks.append(position('Y', '<', ymax))
        # The loader preserves condition order: these run before any lookup.
        result.append('[' + '&'.join(checks + terms) + ']' + body)
        guarded += bool(checks)
    index = next(i for i, line in enumerate(result) if '<tile>' in line)
    result[index:index] = declarations
    return result, {'guarded_rules': guarded, 'position_conditions': len(declarations)}


def build(dest, enemy_records=None, slime_sheet=None):
    previous_build(dest, door_backing=ROOT/'art/area2-door-interior-v0112.png',
                   enemy_records=enemy_records, slime_sheet=slime_sheet)
    lines, report = guard_area2_neighbors((dest/'hires.txt').read_text().splitlines())
    lines[0] = '# Bionic Commando HD v0.11.2 - opaque doorway and bounded Area 2 lookups'
    lines = [line.replace('<img>area2-polish-v0111.png', '<img>area2-polish-v0112.png') for line in lines]
    (dest/'area2-polish-v0111.png').replace(dest/'area2-polish-v0112.png')
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    text = (dest/'README.txt').read_text().replace('v0.11.1', 'v0.11.2')
    text = text.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nOpaque dark outpost doorway. Bounded Area 2 neighbor lookups prevent\nthe one-past-screen read exposed while entering the first doorway.\n\n')
    (dest/'README.txt').write_text(text)
    (ROOT/'validation/v0112-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    build(parser.parse_args().output)


if __name__ == '__main__':
    main()
