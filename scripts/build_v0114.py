"""Complete the Area 2 outlet, long pipe and late doorway variants."""
from pathlib import Path
import argparse
import json
import re
from PIL import Image
from build_v0113 import build as previous_build
from build_v0111 import cell, fit, CAVE
from build_v0112 import guard_area2_neighbors

ROOT = Path(__file__).resolve().parents[1]
PALETTE = 0x0F2B1C0B


def build(dest):
    previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    # Recompute all bounds once, after adding the newly observed layouts.
    lines = [re.sub(r'a212Bound\d+&', '', line) for line in lines
             if not line.startswith('<condition>a212Bound')]
    images = [Image.open(dest/line[5:]).convert('RGBA') for line in lines if line.startswith('<img>')]
    index = len(images)
    atlas = Image.new('RGBA', (2048, 512))
    cells, rules, conditions, neighbors = {}, [], [], {}
    catalog = json.loads((ROOT/'capture/area2/material-catalog.json').read_text())
    ids = {e['index']: e['key'] for e in catalog if e['layer'] == 0 and e['palette'] == '0F2B1C0B'}
    structures = Image.open(ROOT/'art/area2-structures-v0111.png').convert('RGBA')
    art = [cell(structures, n, main_component=True) for n in range(6)]
    slime = Image.open(ROOT/'art/area2-blue-slime-v0113.png').convert('RGBA')

    def emit(k, im, tests=()):
        assert im.size == (32, 32)
        data = im.tobytes()
        if data not in cells:
            n = len(cells)
            cells[data] = n % 64 * 32, n // 64 * 32
            atlas.paste(im, cells[data])
        x, y = cells[data]
        rules.append(f'[{CAVE}' + ''.join('&'+t for t in tests) + f']<tile>{index},{k},{PALETTE:08X},{x},{y},1,N')

    def piece(im, x, y):
        return im.crop((x*4, y*4, (x+8)*4, (y+8)*4))

    def nearby(dx, dy, key):
        signature = dx, dy, key
        if signature not in neighbors:
            name = f'a214Near{len(neighbors)}'
            neighbors[signature] = name
            conditions.append(f'<condition>{name},tileNearby,{dx},{dy},{key},{PALETTE:08X},N')
        return neighbors[signature]

    def entries(n):
        return [(int(a[1]), int(a[2]), a[3]) for a in
                (s.split(',') for s in (ROOT/f'capture/area2-v0114/{n:05}.tiles').read_text().splitlines())
                if a[0] == '0' and int(a[4]) == PALETTE]

    # This standalone round opening has four different CHR patterns from the
    # tall drain. It needs just the mouth, without the long backing panel.
    mouth = art[3].crop((0, 0, art[3].width, art[3].width))
    round_outlet = fit(mouth, (64, 64))
    for i, x, y in [(96, 0, 0), (92, 8, 0), (97, 0, 8), (93, 8, 8)]:
        emit(ids[i], piece(round_outlet, x, y))

    # The final doorway's emblem/header uses a third set of patterns. Reuse
    # the already approved grille and jamb placement, retaining the opening.
    door = fit(art[1], (128, 192))
    door.paste(fit(art[1].crop((0, 0, art[1].width, round(art[1].height*.25))), (128, 32)), (0, 0))
    for x, y, k in entries(9601):
        if 56 <= x < 88 and 174 <= y < 190 and k != '0'*32:
            emit(k, piece(door, x-56, y-174))

    # The long disconnected leg below the platform has two repeated shaft
    # sections, not the one-section leg in the first U-pipe sample.
    pipe = fit(art[2], (384, 320)).crop((0, 128, 128, 320))
    # Use the same backing brick as the existing pipe assembly.
    old_rule = next(line for line in lines if '<tile>' in line and line.split('<tile>')[1].split(',')[1:3] == [ids[0], f'{PALETTE:08X}'])
    fields = old_rule.split('<tile>')[1].split(',')
    ix, iy = map(int, fields[3:5])
    brick = images[int(fields[0])].crop((ix, iy, ix+32, iy+32))
    def backed(im):
        under = brick.copy()
        under.alpha_composite(im)
        return under
    selected = [(x, y, k) for x, y, k in entries(9361) if 51 <= x < 83 and 174 <= y < 222]
    anchors = [(x, y, k) for x, y, k in selected if k in {ids[i] for i in (88, 89, 90, 91)}]
    for x, y, k in selected:
        under = brick.copy()
        under.alpha_composite(piece(pipe, x-51, y-174))
        for ax, ay, ak in sorted(anchors, key=lambda a: abs(a[0]-x)+abs(a[1]-y))[:2]:
            emit(k, under, [nearby(ax-x, ay-y, ak)])

    # The earlier wide-U mapping painted a detached right shaft into the
    # black platform underside here. Two native anchors identify the longer
    # left leg and retain the actual empty underside in this layout only.
    for x, y, k in entries(9361):
        if 83 <= x < 163 and y == 174 and k == ids[4]:
            emit(k, Image.new('RGBA', (32, 32)),
                 [nearby(51-x, 206-y, ids[88]), nearby(51-x, 182-y, ids[53])])

    # Tall native flow repeats an eight-cell block. Select complete vertical
    # ribbon slices when the nozzle is present, with a vertical fallback for
    # the portions continuing below platforms or entering at the screen edge.
    ribbon = fit(cell(slime, 4, main_component=True), (128, 192))
    column = Image.new('RGBA', (128, 192))
    column.alpha_composite(fit(mouth, (128, 64)), (0, 0))
    column.alpha_composite(fit(cell(slime, 4, main_component=True), (96, 160)), (16, 32))
    selected = [(x, y, k) for x, y, k in entries(2401) if 100 <= x < 132 and 135 <= y < 183]
    header_keys = {ids[i] for i in range(98, 106)}
    anchors = [(x, y, k) for x, y, k in selected if k in header_keys]
    for x, y, k in selected:
        im = backed(piece(column, x-100, y-135))
        if k in header_keys:
            emit(k, im)
        else:
            for ax, ay, ak in sorted(anchors, key=lambda a: abs(a[0]-x)+abs(a[1]-y))[:2]:
                emit(k, im, [nearby(ax-x, ay-y, ak)])
    for i in range(26, 34):
        emit(ids[i], backed(ribbon.crop(((i-26)%4*32, 64+(i-26)//4*32,
                                        (i-26)%4*32+32, 96+(i-26)//4*32))))

    # When the long leg's elbow is outside the viewport, its visible shaft
    # must still be painted. Keep existing complete/narrow assemblies first.
    split = len(rules)
    for i, x, y in [(51, 0, 0), (48, 8, 0), (53, 0, 8), (52, 8, 8)]:
        emit(ids[i], backed(piece(pipe, x, y)))
    for y, anchor, left_ids, right_ids in [(0, 51, (4, 10), (4, 7)),
                                         (8, 53, (6, 12), (5, 11))]:
        for x, candidates in [(16, left_ids), (24, right_ids)]:
            for i in candidates:
                emit(ids[i], backed(piece(pipe, x, y)), [nearby(-x, 0, ids[anchor])])
    fallbacks = rules[split:]
    rules = rules[:split]
    after = max(i for i, line in enumerate(lines) if '<tile>' in line and
                line.split('<tile>')[1].split(',')[0] == '11') + 1
    lines[after:after] = fallbacks

    at = next(i for i, line in enumerate(lines) if '<tile>' in line)
    lines[at:at] = ['<img>area2-layouts-v0114.png'] + conditions + list(dict.fromkeys(rules))
    lines, bounds = guard_area2_neighbors(lines)
    lines[0] = '# Bionic Commando HD v0.11.4 - complete Area 2 machinery and slime layouts'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0, 0, 2048, ((len(cells)+63)//64)*32)).save(dest/'area2-layouts-v0114.png')
    readme = (dest/'README.txt').read_text().replace('v0.11.3', 'v0.11.4')
    readme = readme.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nComplete late doorway header, round outlets and extended lower pipe.\nTall blue slime flow uses connected vertical art instead of stacked pools.\n\n', 1)
    (dest/'README.txt').write_text(readme)
    report = {'version': '0.11.4', 'layout_rules': len(set(rules)),
              'clipped_pipe_fallbacks': len(fallbacks), 'art_cells': len(cells),
              'reference_frames': [2401, 9361, 9601], 'bounds': bounds,
              'scope': 'Area 2 cave background palette 0F2B1C0B only'}
    (ROOT/'validation/v0114-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    build(parser.parse_args().output)


if __name__ == '__main__':
    main()
