"""Area 3 corrections: pendant, powder snow, distant tile and reused boss."""
from pathlib import Path
import argparse
import json
import shutil
from PIL import Image
from build_v0120 import build as previous_build, OUT, NORMAL
from build_v0112 import guard_area2_neighbors
from build_v0111 import fit

ROOT = Path(__file__).resolve().parents[1]


def build(dest, reuse=False):
    dest.mkdir(parents=True, exist_ok=True)
    if reuse:
        for p in dest.iterdir():
            p.unlink()
        for p in (ROOT.parent/'output/v0120-extracted').iterdir():
            shutil.copy2(p, dest/p.name)
    else:
        previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    images = [s[5:] for s in lines if s.startswith('<img>')]
    image_id = len(images)
    atlas = Image.new('RGBA', (512, 256))
    cells, rules = {}, []
    edge_conditions = []

    def emit(key, palette, image, guard):
        raw = image.tobytes()
        if raw not in cells:
            n = len(cells)
            xy = n % 16 * 32, n // 16 * 32
            cells[raw] = xy
            atlas.paste(image, xy)
        x, y = cells[raw]
        rules.append(f'[{guard}]<tile>{image_id},{key},{palette:08X},{x},{y},1,N')

    # These four patterns are the cross pendant, not a field communicator.
    pendant = Image.open(ROOT/'art/area3-cross-pendant-v0121.png').convert('RGBA')
    box = pendant.getchannel('A').point(lambda a: 255 if a > 32 else 0).getbbox()
    pendant = fit(pendant.crop(box), (64, 64))
    keys = [
        ['0D00181111C080000000060F0F3F7FFF', 'C0201804042222220000000000E0E0E0'],
        ['E10101010101011FFF1F1F1F1F1F1F1F', 'C12121212121121CC000000000000000'],
    ]
    for y, row in enumerate(keys):
        for x, key in enumerate(row):
            tile = pendant.crop((x*32, y*32, x*32+32, y*32+32))
            for guard in ['area3&equipment', 'area3&worldmap']:
                emit(key, 0xFF30260F, tile, guard)

    # Index 70 is the final distant mountain fragment at the tree approach.
    # It belongs to the replaced panorama, not the interactive rock wall.
    catalog = json.loads((ROOT/'capture/area3/material-catalog.json').read_text())
    snowkeys = {r['index']: r['key'] for r in catalog
                if r['layer'] == 0 and r['palette'] == '1C201000'}
    emit(snowkeys[70], 0x1C201000, Image.new('RGBA', (32, 32)), OUT)

    # The snow field is two columns and four visible bands, followed by one
    # repeated solid fill tile. Sample soft powder at consistent native joins.
    # Retain native collision/sinking logic and the existing sprite priority.
    snow = Image.open(ROOT/'art/area3-soft-snow-v0121.png').convert('RGBA')
    snow = fit(snow, (64, 128))
    for y, row in enumerate([[51, 56], [52, 57], [53, 58], [54, 59]]):
        for x, index in enumerate(row):
            tile = snow.crop((x*32, y*32, x*32+32, y*32+32))
            emit(snowkeys[index], 0x1C201000, tile, OUT)
    emit(snowkeys[55], 0x1C201000, snow.crop((16, 80, 48, 112)), OUT)

    # At the extreme right the native renderer clamps the final exhaust
    # cells to x=0 for another two head positions beyond the older wrap
    # repair's range. Suppress only those cells, with the head positively
    # identified across the screen; all lookups remain in bounds.
    edge_conditions += ['<condition>a3121WrapX,positionCheckX,<,8',
                        '<condition>a3121WrapY,positionCheckY,>=,32']
    clipped = [('00D0B8FCA8C2B11CC2204200563D4AE3', 24),
               ('000000000000000000B080E0F098E000', 24),
               ('CC80C4B038100804107E3A4CC4ECF65A', 32),
               ('0000000000000000B080404000000000', 32)]
    head = 'C7C7C7D7C7C7C7FF4141796979797979'
    for headx in [232, 233]:
        for palette in [0xFF202A0F, 0xFF30150F, 0xFF30210F, 0xFF36060F]:
            for dy in [24, 32]:
                name = f'a3121WrapHead{headx}_{palette:08X}_{dy}'
                edge_conditions.append(f'<condition>{name},spriteNearby,{headx},-{dy},{head},{palette:08X},N')
                for key, offset in clipped:
                    if offset == dy:
                        emit(key, palette, Image.new('RGBA', (32, 32)),
                             f'a3121WrapX&a3121WrapY&{NORMAL}&!hmirror&!vmirror&{name}')
    # The same three-frame clamp also affects the robot's outer body column.
    # Use captured head-relative signatures so no painted body fragment is
    # duplicated on the opposite edge when the boss crosses the right side.
    edge_conditions.append('<condition>a3121WrapBottom,positionCheckY,<,232')
    wrapped = json.loads((ROOT/'capture/area3/boss-wrapped-v0121.json').read_text())
    for i, rec in enumerate(wrapped):
        assert not rec['hmirror'] and not rec['vmirror']
        name = f'a3121WrapBody{i}'
        edge_conditions.append(f'<condition>{name},spriteNearby,{rec["dx"]},{rec["dy"]},{head},{rec["head_palette"]:08X},N')
        emit(rec['key'], rec['palette'], Image.new('RGBA', (32, 32)),
             f'a3121WrapX&a3121WrapY&a3121WrapBottom&{NORMAL}&!hmirror&!vmirror&{name}')

    # Reuse the already approved Area 5 robot, including the corrected fixed
    # rear nozzle and native-timed exhaust. Keep original image coordinates,
    # palette variants, pose tests and additional-sprite destinations intact.
    records = json.loads((ROOT/'capture/area5boss-poses.json').read_text())
    native = {r['head'] for r in records} | {t[2] for r in records for t in r['parts']}
    additions = [s[10:].split(',') for s in lines if s.startswith('<addition>')]
    virtual = {a[4] for a in additions if a[0] in native}
    bosskeys = native | virtual
    bossrules = []
    # Four recessed machinery details in the same room also have approved
    # Area 5 paintings; their generic fallback leaves flat brown pixels.
    roomkeys = {
        '000000003E000000000000003E000000', '18180000000000001818000000120000',
        '00000000300000000000000030000000', '30003000300000003000300030000000',
    }
    roomrules = []
    for line in lines:
        if not (line.startswith('[') and '<tile>' in line):
            continue
        guard, body = line[1:].split(']', 1)
        terms = guard.split('&')
        tile = body[6:].split(',')
        key = tile[1]
        exhaust = images[int(tile[0])] == 'area5-exhaust-v098.png'
        if 'area5' in terms and (key in bosskeys or exhaust):
            terms = ['area3' if t == 'area5' else t for t in terms]
            bossrules.append('['+'&'.join(terms)+']'+body)
        elif 'area5' in terms and key in roomkeys and tile[2] == '0F372716':
            terms = ['area3' if t == 'area5' else t for t in terms]
            roomrules.append('['+'&'.join(terms)+']'+body)
    assert len(bossrules) == 3296, len(bossrules)
    assert len(roomrules) == 4, len(roomrules)
    # Bound exhaust mirror cases separately. Intersecting both directions
    # rejects valid leftward lookups near the right edge (and disables the
    # wrapped-fragment suppression entirely). Preserve all four orientations.
    expanded = []
    for line in bossrules:
        if 'exhaust098' in line:
            guard, body = line[1:].split(']', 1)
            for mirror in ['!hmirror', 'hmirror']:
                for vertical in ['!vmirror', 'vmirror']:
                    expanded.append('['+guard+'&'+mirror+'&'+vertical+']'+body)
        else:
            expanded.append(line)
    bossrules = expanded
    # Rebound inherited neighbor tests for this area without modifying any
    # older rule or reusing a prior patch's position-condition names.
    inherited = [s for s in lines if s.startswith('<condition>') and
                 (',spriteNearby,' in s or ',tileNearby,' in s)]
    guarded, bounds = guard_area2_neighbors(
        inherited + [s.replace('[area3&', '[area2&') for s in bossrules])
    guarded = [s.replace('a212Bound', 'a3121Bound').replace('&area2&', '&area3&')
               .replace('[area2&', '[area3&') for s in guarded if s not in inherited]
    declarations = [s for s in guarded if s.startswith('<condition>')]
    bossrules = [s for s in guarded if not s.startswith('<condition>')]
    insertion = next(i for i, s in enumerate(lines) if '<tile>' in s)
    lines[insertion:insertion] = ['<img>area3-fixes-v0121.png'] + declarations + edge_conditions + rules + roomrules + bossrules
    lines[0] = '# Bionic Commando HD v0.12.1 - Area 3 pendant, snow and reused robot'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0, 0, 512, max(32, (len(cells)+15)//16*32))).save(dest/'area3-fixes-v0121.png')
    readme = (dest/'README.txt').read_text().replace('v0.12.0', 'v0.12.1')
    readme = readme.replace('NEW IN THIS BUILD\n',
        'NEW IN THIS BUILD\nCross pendant inventory icon, softer sinking snow, removal of the stray\n'
        'mountain tile beside the tree, and the previously approved robot boss\n'
        'with its fixed nozzle and native-timed exhaust.\n\n', 1)
    (dest/'README.txt').write_text(readme)
    report = {'version': '0.12.1', 'pendant_rules': 8, 'snow_rules': 9,
              'removed_distant_fragments': 1, 'reused_boss_source_rules': 3296,
              'reused_boss_rules': len(bossrules),
              'reused_room_detail_rules': len(roomrules),
              'additional_clipped_exhaust_rules': 32,
              'additional_clipped_body_rules': len(wrapped),
              'new_sprite_additions': 0, 'boss_art_modified': False,
              'bounds': bounds, 'new_atlas_cells': len(cells)}
    (ROOT/'validation/v0121-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    parser.add_argument('--reuse-approved', action='store_true')
    args = parser.parse_args()
    build(args.output, args.reuse_approved)


if __name__ == '__main__':
    main()
