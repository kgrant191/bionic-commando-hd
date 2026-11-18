"""Area 3 recessed backgrounds, open entrance and complete boss blast."""
from pathlib import Path
import argparse, ctypes, json, shutil
import numpy as np
from PIL import Image, ImageOps
from build_v0121 import build as previous_build
from build_v0120 import OUT, NORMAL, indices, guard_neighbors
from build_v0111 import cell, fit

ROOT = Path(__file__).resolve().parents[1]


def build(dest, reuse=False):
    dest.mkdir(parents=True, exist_ok=True)
    if reuse:
        for p in dest.iterdir(): p.unlink()
        for p in (ROOT.parent/'output/v0121-extracted').iterdir(): shutil.copy2(p, dest/p.name)
    else:
        previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    image_id = sum(s.startswith('<img>') for s in lines)
    atlas = Image.new('RGBA', (1024, 1024))
    cache, rules, conditions, neighbors = {}, [], [], {}

    def emit(key, palette, im, guard):
        assert im.size == (32, 32)
        data = im.tobytes()
        if data not in cache:
            n = len(cache); xy = n % 32 * 32, n // 32 * 32
            cache[data] = xy; atlas.paste(im, xy)
        x, y = cache[data]
        rules.append(f'[{guard}]<tile>{image_id},{key},{palette:08X},{x},{y},1,N')

    def nearby(dx, dy, key, palette, kind='tile'):
        spec = dx, dy, key, palette, kind
        if spec not in neighbors:
            name = f'a3122Near{len(neighbors)}'; neighbors[spec] = name
            conditions.append(f'<condition>{name},{kind}Nearby,{dx},{dy},{key},{palette:08X},N')
        return neighbors[spec]

    # Dark, fine mesh reads as recessed backing rather than grappleable stone.
    # Keep the native outer contours; collision and grapple logic are untouched.
    catalog = json.loads((ROOT/'capture/area3/material-catalog.json').read_text())
    backing = [r for r in catalog if r['layer'] == 0 and r['palette'] == '1C201000' and r['index'] >= 71]
    industry = Image.open(ROOT/'art/area3-industry-v0120.png').convert('RGBA')
    mesh = Image.new('RGBA', (64, 64), (8, 20, 25, 255))
    mesh.alpha_composite(fit(industry.crop((1120, 160, 1450, 490)), (64, 64)))
    mesh = mesh.crop((0, 0, 32, 32))
    scaler = ctypes.CDLL(str(ROOT/'tools/scale.so'))
    scaler.scale4.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    for rec in backing:
        mask = np.uint8(indices(rec['key']) > 0)*255
        src = np.dstack([mask]*4).copy(); target = np.zeros((32, 32, 4), np.uint8)
        scaler.scale4(src.ctypes.data, target.ctypes.data, 8, 8)
        im = mesh.copy(); im.putalpha(Image.fromarray(target[:, :, 3]))
        emit(rec['key'], 0x1C201000, im, OUT)

    # Reuse the approved metal portal and its opaque dark interior. Select
    # repeated fill tiles by the jamb in the same row so ordinary cliff fill
    # does not turn into doorway pieces elsewhere in the stage.
    frame = cell(Image.open(ROOT/'art/area2-structures-v0111.png').convert('RGBA'), 1, main_component=True)
    doorway = fit(Image.open(ROOT/'art/area2-door-interior-v0112.png').convert('RGBA'), (128, 128))
    doorway.alpha_composite(fit(frame, (128, 128)))
    parts = json.loads((ROOT/'capture/area3/door-v0122.json').read_text())
    jambs = {y: (key, pal) for x, y, key, pal in parts if x == 0}
    for x, y, key, pal in parts:
        guard = OUT
        if x in [8, 16]:
            anchor, ap = jambs[y]
            guard += '&'+nearby(-x, 0, anchor, ap)
        emit(key, pal, doorway.crop((x*4, y*4, x*4+32, y*4+32)), guard)

    # The robot's actual death animation is a separate five-pattern family:
    # compact ignition, expanded blast, and dispersing smoke. Paint all 16
    # recorded frames, not only the robot body and projectile/exhaust effects.
    phases = json.loads((ROOT/'capture/area3/boss-explosions-v0122.json').read_text())
    effects = Image.open(ROOT/'art/area2-effects-v0111.png').convert('RGBA')
    previews = ROOT/'validation/pose-previews/area3-explosions-v0122'; previews.mkdir(parents=True, exist_ok=True)
    effectkeys = set()
    for phase, rec in enumerate(phases):
        w, h = rec['size']; painting = fit(cell(effects, phase, main_component=True), (w*4, h*4))
        if phase == 2:
            # The last native pose is eight detached fragments with no
            # center cells. Each needs a complete, softly edged puff;
            # slicing a large cloud across that layout makes square holes.
            puff = fit(cell(effects, 2, main_component=True), (32, 32))
            painting = Image.new('RGBA', (w*4, h*4))
            for x, y, key, pal, hm, vm in rec['parts']:
                effectkeys.add(key)
                part = ImageOps.mirror(puff) if hm else puff
                if vm: part = ImageOps.flip(part)
                painting.alpha_composite(part, (x*4, y*4))
            emit(rec['parts'][0][2], rec['parts'][0][3], puff, NORMAL)
            painting.save(previews/f'{phase}.png')
            continue
        painting.save(previews/f'{phase}.png')
        for x, y, key, pal, hm, vm in rec['parts']:
            effectkeys.add(key)
            im = painting.crop((x*4, y*4, x*4+32, y*4+32))
            if hm: im = ImageOps.mirror(im)
            if vm: im = ImageOps.flip(im)
            guard = NORMAL + ('&hmirror' if hm else '&!hmirror') + ('&vmirror' if vm else '&!vmirror')
            emit(key, pal, im, guard)

    new, safety = guard_neighbors(conditions+list(dict.fromkeys(rules)), lines)
    new = [s.replace('a3120Bound', 'a3122Bound') for s in new]
    at = next(i for i, s in enumerate(lines) if '<tile>' in s)
    lines[at:at] = ['<img>area3-surfaces-v0122.png'] + new
    lines[0] = '# Bionic Commando HD v0.12.2 - recessed backgrounds, entrance and boss explosion'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0, 0, 1024, max(32, (len(cache)+31)//32*32))).save(dest/'area3-surfaces-v0122.png')
    readme = (dest/'README.txt').read_text().replace('v0.12.1', 'v0.12.2')
    readme = readme.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nDark recessed grilles distinguish decorative wall insets from solid rock.\nThe outdoor entrance has a metal frame and opaque dark interior.\nAll three robot destruction phases use painted explosion and smoke art.\n\n', 1)
    (dest/'README.txt').write_text(readme)
    report = {'version': '0.12.2', 'new_rules': len(set(rules)), 'art_cells': len(cache),
              'recess_keys': [r['key'] for r in backing], 'door_cells': 16,
              'explosion_keys': sorted(effectkeys), 'explosion_phases': 3,
              'explosion_frames': list(range(9852, 9868)), 'bounds': safety,
              'new_sprite_additions': 0, 'new_art_generation': False}
    (ROOT/'validation/v0122-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if not k.endswith('keys') and k != 'explosion_frames'}), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, default=ROOT/'pack')
    parser.add_argument('--reuse-approved', action='store_true'); a = parser.parse_args(); build(a.output, a.reuse_approved)


if __name__ == '__main__': main()
