"""Recover world-locked material phases from the native Area 3 recording."""
from pathlib import Path
from collections import Counter, defaultdict, deque
import json
from build_v0120 import indices

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT/'capture/area3/material-catalog.json').read_text())
    palettes = {0x1C271707, 0x1C201707, 0x1C302907}
    # Flat fill repeats at arbitrary positions; door art has its own assembly.
    excluded = {r['key'] for r in catalog if r['layer'] == 0 and
                (len(set(indices(r['key']).flat)) == 1 or
                 (r['palette'] == '1C201707' and r['index'] >= 74))}
    wanted = {r['key'] for r in catalog if r['layer'] == 0 and
              int(r['palette'], 16) in palettes} - excluded
    edges = Counter()
    frames = 0
    for n in range(1044, 5060):
        path = ROOT.parent/f'replay-area3/original-dense/tiles/{n:05}.tiles'
        grid = {}
        for line in path.read_text().splitlines():
            layer, x, y, key, pal, hm, vm = line.split(',')
            if layer == '0' and key in wanted and int(pal) in palettes:
                grid[int(x), int(y)] = key
        if not grid:
            continue
        frames += 1
        for (x, y), key in grid.items():
            for dx, dy in [(8, 0), (0, 8)]:
                neighbor = grid.get((x+dx, y+dy))
                if neighbor:
                    edges[key, neighbor, dx//8, dy//8] += 1
    graph = defaultdict(list)
    for key, neighbor, dx, dy in edges:
        graph[key].append((neighbor, dx, dy))
        graph[neighbor].append((key, -dx, -dy))
    positions, components = {}, 0
    for first in sorted(graph):
        if first in positions:
            continue
        components += 1
        positions[first] = [0, 0]
        queue = deque([first])
        while queue:
            key = queue.popleft()
            x, y = positions[key]
            for neighbor, dx, dy in graph[key]:
                value = [(x+dx) % 2, (y+dy) % 2]
                if neighbor in positions:
                    assert positions[neighbor] == value, (key, neighbor)
                else:
                    positions[neighbor] = value
                    queue.append(neighbor)
    report = {'recorded_frames_checked': frames, 'unique_adjacencies': len(edges),
              'components': components, 'texture_period_tiles': [2, 2],
              'excluded_flat_or_door_patterns': sorted(excluded & {r['key'] for r in catalog
                  if r['layer'] == 0 and int(r['palette'], 16) in palettes}),
              'positions': positions}
    (ROOT/'capture/area3/terrain-layout-v0125.json').write_text(json.dumps(report, indent=2)+'\n')
    print({k: v for k, v in report.items() if k not in ['positions', 'excluded_flat_or_door_patterns']})


if __name__ == '__main__':
    main()
