"""Replace Area 3 decorative mesh with frost-tipped alpine vegetation."""
from pathlib import Path
import argparse, ctypes, json, shutil
import numpy as np
from PIL import Image
from build_v0122 import build as previous_build
from build_v0120 import OUT, indices

ROOT = Path(__file__).resolve().parents[1]


def build(dest, reuse=False):
    dest.mkdir(parents=True, exist_ok=True)
    if reuse:
        for p in dest.iterdir(): p.unlink()
        for p in (ROOT.parent/'output/v0122-extracted').iterdir():
            shutil.copy2(p, dest/p.name)
    else:
        previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    image_id = sum(s.startswith('<img>') for s in lines)
    layout = json.loads((ROOT/'capture/area3/vegetation-layout-v0123.json').read_text())
    texture = Image.open(ROOT/'art/area3-winter-vegetation-v0123.png').convert('RGBA')
    texture = texture.resize((64, 64), Image.Resampling.LANCZOS)
    atlas = Image.new('RGBA', (1024, 1024)); cells = {}; rules = []
    scaler = ctypes.CDLL(str(ROOT/'tools/scale.so'))
    scaler.scale4.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    for key, (tx, ty) in sorted(layout['positions'].items()):
        # The native pattern adjacency determines the 2x2 texture phase.
        # It remains fixed to the world while the camera scrolls.
        mask = np.uint8(indices(key) > 0)*255
        src = np.dstack([mask]*4).copy(); target = np.zeros((32, 32, 4), np.uint8)
        scaler.scale4(src.ctypes.data, target.ctypes.data, 8, 8)
        im = texture.crop((tx*32, ty*32, tx*32+32, ty*32+32))
        im.putalpha(Image.fromarray(target[:, :, 3]))
        data = im.tobytes()
        if data not in cells:
            n = len(cells); xy = (n % 32 * 32, n // 32 * 32)
            cells[data] = xy; atlas.paste(im, xy)
        x, y = cells[data]
        rules.append(f'[{OUT}]<tile>{image_id},{key},1C201000,{x},{y},1,N')
    at = next(i for i, s in enumerate(lines) if '<tile>' in s)
    lines[at:at] = ['<img>area3-vegetation-v0123.png'] + rules
    lines[0] = '# Bionic Commando HD v0.12.3 - winter alpine vegetation'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0, 0, 1024, max(32, (len(cells)+31)//32*32))).save(dest/'area3-vegetation-v0123.png')
    readme = (dest/'README.txt').read_text().replace('v0.12.2', 'v0.12.3')
    readme = readme.replace('Dark recessed grilles distinguish decorative wall insets from solid rock.',
        'Frost-tipped alpine moss and evergreen foliage replace the decorative wall mesh.\nVegetation stays distinct from the solid brown rock and snowy ledges.')
    (dest/'README.txt').write_text(readme)
    report = {'version': '0.12.3', 'new_rules': len(rules), 'art_cells': len(cells),
              'texture_period_tiles': [2, 2], 'new_conditions': 0,
              'new_sprite_additions': 0, 'native_contours_preserved': True,
              'keys': sorted(layout['positions'])}
    (ROOT/'validation/v0123-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'keys'}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    parser.add_argument('--reuse-approved', action='store_true')
    a = parser.parse_args(); build(a.output, a.reuse_approved)


if __name__ == '__main__': main()
