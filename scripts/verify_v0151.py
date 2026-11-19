"""Verify the Area 8 regression against the recorded inputs and the installed review package."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from PIL import Image, ImageChops

from verify_v0110 import structure

FRAME_COUNT = 24505

def digest(path):
    h = sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def same_state(original, *replays, frames):
    for run in (original, *replays):
        assert int((run / 'home/done').read_text()) == frames, run
        assert not re.search(r'\[HDPack\].*(?:error|invalid|unable)|script error|exception',
                             (run / 'log').read_text(), re.I), run
    for file, width in [('ram.bin', 2048), ('palette.bin', 32), ('oam.bin', 256)]:
        assert (original/file).stat().st_size == width*frames
        expected = digest(original/file)
        for run in replays:
            assert digest(run/file) == expected, (file, run)


def raw_count(path):
    # The replay trace contains five fields per observed tile: frame, key index,
    # number of visible native pixels, first X and first Y.
    distinct = set()
    for line in path.read_text().splitlines():
        frame, key, count, x, y = map(int, line.split())
        assert 1 <= frame <= FRAME_COUNT and count > 0
        distinct.add(key)
    return len(distinct)


def verify(original, before, final, scan, control, catalogue, prior_town, current_town, pack, archive):
    same_state(original, before, final, scan, frames=FRAME_COUNT)
    same_state(prior_town, current_town, frames=4385)
    control_hits = raw_count(control/'matched.tsv')
    assert control_hits > 0
    assert raw_count(scan/'matched.tsv') == 0

    stats = structure(pack)
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert {Path(row).name for row in z.namelist()} == {f.name for f in pack.iterdir() if f.is_file()}
        for row in z.namelist():
            assert z.read(row) == (pack/Path(row).name).read_bytes()
    checked = changed = guarded = 0
    for old in sorted((before/'frames').glob('*.png')):
        n = int(old.stem)
        new = final/'frames'/old.name
        assert new.is_file(), old.name
        checked += 1
        different = old.read_bytes() != new.read_bytes()
        changed += different
        if n <= 575 or n >= 24330:
            assert not different, ('map and equipment', n)
            guarded += 1
        if n in (2020, 6288, 10392, 11712, 16920, 23325, 24000):
            assert different, ('unchanged target', n)
        if n in (12288, 19056, 24000):
            with Image.open(old) as left, Image.open(new) as right:
                delta = ImageChops.difference(left.convert('RGB'), right.convert('RGB'))
            assert delta.getbbox()
            if n==24000:
                a,b,c,d = delta.getbbox()
                assert 280<=a<c<=356 and 124<=b<d<=164, ('clear text escaped its two digits', delta.getbbox())
            else:
                assert not delta.crop((704,0,1024,438)).getbbox(), ('radio portrait', n)
                assert not delta.crop((0,440,1024,896)).getbbox(), ('radio console', n)
    towns = sorted((prior_town/'frames').glob('*.png'))
    assert len(towns) >= 182
    for old in towns:
        assert old.read_bytes() == (current_town/'frames'/old.name).read_bytes(), old.name
    return {
        'area8_recorded_frames': FRAME_COUNT, 'identical_game_state_frames': FRAME_COUNT,
        'native_pattern_palette_pairs_in_trace_catalogue': len(json.loads(gzip.decompress(catalogue.read_bytes()))),
        'positive_control_native_pairs_in_earlier_test_build': control_hits,
        'visible_original_matches_in_final_trace': 0,
        'v0150_and_v0151_screenshot_pairs': checked, 'changed_screenshot_pairs': changed,
        'byte_identical_map_and_equipment_samples': guarded, 'unchanged_area14_samples': len(towns),
        'area14_recorded_frames': 4385, 'archive_sha256': digest(archive),
        'runtime_structure': stats
    }


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('original','before','final','scan','control','catalogue','prior_town','current_town','pack','archive'):
        parser.add_argument(key,type=Path)
    print(json.dumps(verify(**vars(parser.parse_args())),indent=2))
