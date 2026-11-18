"""Separate passable snow patches from solid stone and restore plant warnings."""
from pathlib import Path
import argparse, ctypes, json, shutil
import numpy as np
from PIL import Image
from build_v0125 import build as previous_build
from build_v0120 import OUT, indices
from build_v0111 import fit

ROOT = Path(__file__).resolve().parents[1]
WARNING_KEYS = [
    ['83CF79DFEF7BA6035C108620108418FC', '1824220200000000E69915746E6A4A88'],
    ['83D7FAFCF2E150085C2801010D122DF3', '0301000000000000B06E6D454D080800'],
]


def build(dest, reuse=False):
    dest.mkdir(parents=True, exist_ok=True)
    if reuse:
        for p in dest.iterdir(): p.unlink()
        for p in (ROOT.parent/'output/v0125-extracted').iterdir(): shutil.copy2(p, dest/p.name)
    else:
        previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    image_id = sum(s.startswith('<img>') for s in lines)
    atlas = Image.new('RGBA', (1024, 128))
    cells, rules, changed = {}, [], []

    def emit(key, palette, im):
        assert im.size == (32, 32)
        data = im.tobytes()
        if data not in cells:
            n = len(cells); xy = n % 32 * 32, n // 32 * 32
            cells[data] = xy; atlas.paste(im, xy)
        x, y = cells[data]
        rules.append(f'[{OUT}]<tile>{image_id},{key},{palette:08X},{x},{y},1,N')
        changed.append([key, f'{palette:08X}'])

    source = Image.open(ROOT/'art/area3-classic-materials-v0125.png').convert('RGBA')
    w, h = source.size
    snow = fit(source.crop((w//2, h//2, w, h)), (64, 64))
    phases = json.loads((ROOT/'capture/area3/terrain-layout-v0125.json').read_text())['positions']
    catalog = json.loads((ROOT/'capture/area3/material-catalog.json').read_text())
    # Native indices 71–82 are snowy, passable cliff markings; 83–140 are
    # actual stone barriers. Their common palette does not imply common use.
    passable = [r for r in catalog if r['layer'] == 0 and
                r['palette'] == '1C201000' and 71 <= r['index'] <= 82]
    solid = [r for r in catalog if r['layer'] == 0 and
             r['palette'] == '1C201000' and r['index'] >= 83]
    scaler = ctypes.CDLL(str(ROOT/'tools/scale.so'))
    scaler.scale4.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    for rec in passable:
        key = rec['key']; x, y = phases[key]
        im = snow.crop((x*32, y*32, x*32+32, y*32+32))
        mask = np.uint8(indices(key) > 0)*255
        src = np.dstack([mask]*4).copy(); target = np.zeros((32, 32, 4), np.uint8)
        scaler.scale4(src.ctypes.data, target.ctypes.data, 8, 8)
        im.putalpha(Image.fromarray(target[:, :, 3])); emit(key, 0x1C201000, im)

    # These are the game's two animated pre-emergence frames, not static
    # foreground ledge fragments. Repeated native columns form the full
    # warning strip; the game controls phase, position, mirror and duration.
    art = Image.open(ROOT/'art/area3-plant-warning-v0126.png').convert('RGBA')
    aw, ah = art.size
    frames = [art.crop((i*aw//2, 0, (i+1)*aw//2, ah)) for i in range(2)]
    boxes = [im.getchannel('A').point(lambda a: 255 if a > 24 else 0).getbbox() for im in frames]
    box = min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)
    preview = ROOT/'validation/pose-previews/area3-warning-v0126'; preview.mkdir(parents=True, exist_ok=True)
    for phase, im in enumerate(frames):
        im = fit(im.crop(box), (32, 64)); im.save(preview/f'{phase}.png')
        for row, key in enumerate(WARNING_KEYS[phase]):
            emit(key, 0xFF30290F, im.crop((0, row*32, 32, row*32+32)))

    at = next(i for i, s in enumerate(lines) if '<tile>' in s)
    lines[at:at] = ['<img>area3-readability-v0126.png'] + rules
    lines[0] = '# Bionic Commando HD v0.12.6 - solid terrain and plant spawn warnings'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0, 0, 1024, max(32, (len(cells)+31)//32*32))).save(dest/'area3-readability-v0126.png')
    notes = (dest/'README.txt').read_text().replace('v0.12.5', 'v0.12.6')
    notes = notes.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nSoft snow marks walk-through cliff patches; solid barriers retain gray stone.\nChurning snow, turf and soil visibly warn before giant plants emerge.\n\n', 1)
    notes = notes.replace('Muted gray rock distinguishes recessed backing from solid foreground terrain.',
                          'Gray rock is reserved for solid barriers; passable patches use soft snow.')
    (dest/'README.txt').write_text(notes)
    report = {'version': '0.12.6', 'new_rules': len(rules), 'art_cells': len(cells),
              'new_conditions': 0, 'new_sprite_additions': 0, 'changed_pairs': changed,
              'passable_snow_keys': [r['key'] for r in passable],
              'preserved_solid_stone_keys': [r['key'] for r in solid],
              'warning_phases': WARNING_KEYS, 'warning_native_footprint_per_column': [8, 16],
              'warning_timing': 'native sprite patterns; no timer substitution'}
    (ROOT/'validation/v0126-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print({k: report[k] for k in ['version', 'new_rules', 'art_cells', 'new_conditions', 'new_sprite_additions']}, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    parser.add_argument('--reuse-approved', action='store_true')
    a = parser.parse_args(); build(a.output, a.reuse_approved)


if __name__ == '__main__':
    main()
