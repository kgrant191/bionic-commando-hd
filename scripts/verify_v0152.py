"""Verify Area 8 screenshot fixes in the installed v0.15.2 movie replay."""
import argparse
import json
from pathlib import Path
import re
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageChops

from verify_v0110 import structure
from verify_v0151 import digest, raw_count, same_state


def changed_pixels(previous, current, regions):
    with Image.open(previous) as before, Image.open(current) as after:
        difference = ImageChops.difference(before.convert('RGB'), after.convert('RGB'))
        return [difference.crop(tuple(4 * coord for coord in region)).getbbox() is not None for region in regions]


def check_spencer(archive_pack, frames, original, frame, x_center, y_center):
    # Confirm that the solid paint inside Spencer's launcher, head and legs is
    # present in the gameplay render at the live sprite position.
    name = 'area8-recoil-weaponRocket-right-v0152.png'
    with Image.open(archive_pack / name) as picture:
        plate = np.asarray(picture.crop(picture.getbbox()).convert('RGBA'))
    with Image.open(frames / f'{frame:05}.png') as picture:
        new = np.asarray(picture.convert('RGB'), dtype=np.int16)
    with Image.open(original / f'{frame:05}.png') as picture:
        before = np.asarray(picture.convert('RGB'), dtype=np.int16)
    yy, xx = np.nonzero(plate[:, :, 3] >= 254)
    yy, xx = yy[::23], xx[::23]
    target = plate[yy, xx, :3].astype(np.int16)
    def similarity(image):
        best = 0.0
        for y in range(y_center-27,y_center+28):
            for x in range(x_center-28,x_center+29):
                match = np.abs(image[y+yy, x+xx] - target).max(axis=1) <= 4
                best = max(best, float(match.mean()))
        return best
    old, new = similarity(before), similarity(new)
    assert new > .85 and new-old > .15, (old, new)
    return {'previous_pixel_match': round(old, 3), 'corrected_pixel_match': round(new, 3)}


def verify(original, before, final, scan, town_before, town_final, pack, archive):
    same_state(original, before, final, scan, frames=24505)
    same_state(town_before, town_final, frames=4385)
    for run in (final, scan, town_final):
        assert not re.search(r'\[(?:HDPack|HD Pack)\].*(?:not found|invalid|error|unable)',
                             (run/'log').read_text(errors='replace'), re.I)
    assert raw_count(scan/'matched.tsv') == 0
    names = [f'area8-recoil-{weapon}-{side}-v0152.png' for side in ('left','right')
             for weapon in ('weaponRocket','weaponWide')]
    stats = structure(pack, {name:(1152,1104) for name in names})
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert {Path(f).name for f in z.namelist()} == {f.name for f in pack.iterdir()}
        assert all(z.read(f) == (pack/Path(f).name).read_bytes() for f in z.namelist())
    old_frames, new_frames = before/'frames', final/'frames'
    checks = changed = protected = 0
    for old in old_frames.glob('*.png'):
        n = int(old.stem)
        new = new_frames/old.name
        differs = new.read_bytes() != old.read_bytes()
        checks += 1
        changed += differs
        if n <= 575 or n >= 23990:
            assert not differs, n
            protected += 1
    targets = {
        808:(8,163,76,224), 901:(97,49,166,137), 916:(99,49,188,135),
        1484:(115,118,228,204), 1941:(79,141,159,202),
        5036:(72,125,140,192), 5038:(72,124,140,192),
        7354:(195,126,245,161), 10462:(106,0,178,67), 10464:(108,0,179,70),
        10061:(76,131,190,202), 11415:(101,164,251,224), 19840:(166,119,256,213),
        22984:(167,131,247,199), 22996:(155,129,251,205),
        23027:(122,86,185,149), 23039:(175,135,252,205),
        23268:(131,108,234,193), 23273:(133,110,225,190)
    }
    for n,crop in targets.items():
        file = f'{n:05}.png'
        assert all(changed_pixels(old_frames/file, new_frames/file, [crop])), n
    towns = list((town_before/'frames').glob('*.png'))
    assert len(towns) >= 182
    assert all(p.read_bytes() == (town_final/'frames'/p.name).read_bytes() for p in towns)
    return {'area8_movie_frames':24505, 'identical_game_state_frames':24505,
            'matched_native_tile_pixels':0, 'before_after_screenshot_pairs':checks,
            'changed_screenshot_pairs':changed, 'changed_target_regions':len(targets),
            'identical_menu_map_and_clear_samples':protected, 'area14_movie_frames':4385,
            'identical_area14_samples':len(towns), 'runtime_structure':stats,
            'equipped_spencer_recovery':{n:check_spencer(pack,new_frames,old_frames,n,x,y)
                                         for n,x,y in [(23273,675,520),(23277,637,513),
                                                       (23278,632,508),(23279,618,506)]},
            'archive_sha256':digest(archive)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('original','before','final','scan','town_before','town_final','pack','archive'):
        parser.add_argument(key, type=Path)
    print(json.dumps(verify(**vars(parser.parse_args())),indent=2))
