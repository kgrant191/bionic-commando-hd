"""Paint continuous Area 3 tree modules inside the original silhouettes."""
from pathlib import Path
import argparse, ctypes, json, shutil
import numpy as np
from PIL import Image, ImageOps
from build_v0126 import build as previous_build
from build_v0120 import OUT, indices
from build_v0111 import fit

ROOT = Path(__file__).resolve().parents[1]


def build(dest, reuse=False):
    dest.mkdir(parents=True, exist_ok=True)
    if reuse:
        for p in dest.iterdir(): p.unlink()
        for p in (ROOT.parent/'output/v0126-extracted').iterdir(): shutil.copy2(p, dest/p.name)
    else:
        previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    image_id = sum(s.startswith('<img>') for s in lines)
    # The painting follows a complete native right-facing tree (64x96 NES
    # pixels). Slice coherent 16x16 modules before slicing their four tiles.
    # Rotating individual 8x8 RGB samples was the source of the old patchwork.
    tree = fit(Image.open(ROOT/'art/area3-tree-v0127.png').convert('RGBA'), (256, 384))
    cap = tree.crop((0, 0, 64, 64))
    junction = tree.crop((0, 64, 64, 128))
    trunk = tree.crop((0, 128, 64, 192))
    branch = tree.crop((64, 64, 128, 128))
    tip = tree.crop((192, 64, 256, 128))
    modules = [
        ('crown', [[9, 15], [10, 16]], cap),
        ('right_junction', [[11, 17], [12, 18]], junction),
        ('trunk', [[13, 19], [14, 20]], trunk),
        ('branch', [[21, 23], [22, 24]], branch),
        ('right_tip', [[25, 27], [26, 28]], tip),
        ('left_tip', [[29, 31], [30, 32]], ImageOps.mirror(tip)),
        ('left_junction', [[37, 39], [38, 40]], ImageOps.mirror(junction)),
    ]
    catalog = json.loads((ROOT/'capture/area3/material-catalog.json').read_text())
    keys = {r['index']: r['key'] for r in catalog if r['layer'] == 0 and r['palette'] == '1C271707'}
    scaler = ctypes.CDLL(str(ROOT/'tools/scale.so'))
    scaler.scale4.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    atlas = Image.new('RGBA', (1024, 32)); rules, mapping = [], {}
    previews = ROOT/'validation/pose-previews/area3-trees-v0127'; previews.mkdir(parents=True, exist_ok=True)
    for name, rows, painting in modules:
        preview = Image.new('RGBA', (64, 64))
        for y, row in enumerate(rows):
            for x, i in enumerate(row):
                key = keys[i]
                im = painting.crop((x*32, y*32, x*32+32, y*32+32))
                mask = np.uint8(indices(key) > 0)*255
                src = np.dstack([mask]*4).copy(); target = np.zeros((32, 32, 4), np.uint8)
                scaler.scale4(src.ctypes.data, target.ctypes.data, 8, 8)
                # Preserve native broken tips, width and all grapple contours.
                im.putalpha(Image.fromarray(target[:, :, 3]))
                tx = len(rules)*32; atlas.paste(im, (tx, 0)); preview.paste(im, (x*32, y*32))
                rules.append(f'[{OUT}]<tile>{image_id},{key},1C271707,{tx},0,1,N')
                mapping[i] = {'key': key, 'module': name, 'atlas_xy': [tx, 0]}
        preview.save(previews/f'{name}.png')
    assert len(rules) == 28
    at = next(i for i, s in enumerate(lines) if '<tile>' in s)
    lines[at:at] = ['<img>area3-trees-v0127.png'] + rules
    lines[0] = '# Bionic Commando HD v0.12.7 - continuous weathered trees'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n'); atlas.save(dest/'area3-trees-v0127.png')
    notes = (dest/'README.txt').read_text().replace('v0.12.6', 'v0.12.7')
    notes = notes.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nContinuous weathered bark and curved grain join the tree trunks and branches.\nOriginal tree silhouettes, branch dimensions and grapple points are preserved.\n\n', 1)
    (dest/'README.txt').write_text(notes)
    report = {'version': '0.12.7', 'new_rules': len(rules), 'art_cells': len(rules),
              'new_conditions': 0, 'new_sprite_additions': 0, 'tree_mapping': mapping,
              'changed_pairs': [[keys[i], '1C271707'] for i in sorted(mapping)],
              'native_contours_preserved': True}
    (ROOT/'validation/v0127-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print({k: report[k] for k in ['version', 'new_rules', 'art_cells', 'new_conditions', 'new_sprite_additions']}, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    parser.add_argument('--reuse-approved', action='store_true')
    a = parser.parse_args(); build(a.output, a.reuse_approved)


if __name__ == '__main__':
    main()
