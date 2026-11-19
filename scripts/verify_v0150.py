"""Verify Area 8 playback, protected screens, tile coordinates and installable archive."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from PIL import Image, ImageChops

from verify_v0110 import structure


def verify(original, before, final, pack, bundle, prior_town=None, current_town=None):
    frames = 24505
    assert int((final / 'home/done').read_text()) == frames
    for name, size in [('ram.bin', 2048), ('oam.bin', 256), ('palette.bin', 32)]:
        raw = (original / name).read_bytes()
        assert len(raw) == frames * size
        assert raw == (before / name).read_bytes() == (final / name).read_bytes(), name
    assert not re.search(r'\[HDPack\].*(?:error|invalid|unable)|script error|exception', (final / 'log').read_text(), re.I)
    with ZipFile(bundle) as archive:
        assert archive.testzip() is None
        files = {Path(name).name for name in archive.namelist()}
        assert files == {f.name for f in pack.iterdir() if f.is_file()}
        for name in archive.namelist():
            assert archive.read(name) == (pack / Path(name).name).read_bytes()
    states = structure(pack)
    guard_ranges = {
        'map_and_loadout': [(1, 575)],
        'radio_rooms_and_speakers': [(11820,11935),(12090,12430),(12610,13170),
                                   (17850,17920),(18080,18490),(18660,19210)],
        'debrief_and_return_map': [(23990,24505)],
    }
    samples = Counter()
    images = sorted((before / 'frames').glob('*.png'))
    changed = 0
    for old in images:
        new = final / 'frames' / old.name
        if not new.is_file():
            continue
        n = int(old.stem)
        different = old.read_bytes() != new.read_bytes()
        changed += different
        for name, ranges in guard_ranges.items():
            if any(low <= n <= high for low, high in ranges):
                if n == 19176:
                    # Four mirrored 8x8 impact tiles at NES (43,163), seen
                    # inside the radio room after returning from dialogue.
                    with Image.open(old) as left, Image.open(new) as right:
                        delta = ImageChops.difference(left.convert('RGB'), right.convert('RGB'))
                    assert delta.getbbox() == (172, 620, 236, 684), (name, n)
                    samples['physical_radio_room_with_updated_impact'] += 1
                    continue
                assert not different, (name, n)
                samples[name] += 1
    assert all(samples[k] for k in guard_ranges)
    report = {
        'movie_frames': frames,
        'identical_ram_oam_and_palette_frames': frames,
        'protected_screen_comparisons': dict(samples),
        'changed_gameplay_samples': changed,
        'runtime': states,
        'archive_sha256': sha256(bundle.read_bytes()).hexdigest(),
    }
    if prior_town and current_town:
        checked = 0
        assert (current_town / 'home/done').read_text() == '4385'
        for img in sorted((current_town / 'frames').glob('*.png')):
            assert img.read_bytes() == (prior_town / 'frames' / img.name).read_bytes(), img.name
            checked += 1
        report['area14_unchanged_samples'] = checked
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('original','before','final','pack','bundle'):
        parser.add_argument(arg, type=Path)
    parser.add_argument('--prior-town', type=Path)
    parser.add_argument('--current-town', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(**vars(args)), indent=2))
