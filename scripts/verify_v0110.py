"""Validate Area 2 runtime structure and an exact extracted-ZIP replay."""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def structure(pack, background_sizes=None):
    background_sizes = background_sizes or {}
    verified_backgrounds = set()
    images, tiles, additions = [], [], []
    anchors = set()
    for line in (pack / 'hires.txt').read_text().splitlines():
        body = line.split(']', 1)[-1] if line.startswith('[') else line
        if body.startswith('<img>'):
            images.append(Image.open(pack / body[5:]))
        elif body.startswith('<background>'):
            filename = body[12:].split(',')[0]
            if filename not in verified_backgrounds:
                with Image.open(pack / filename) as background:
                    assert background.size == background_sizes.get(filename, (1024, 960)), filename
                verified_backgrounds.add(filename)
        elif body.startswith('<tile>'):
            fields = body[6:].split(',')
            index, x, y = int(fields[0]), int(fields[3]), int(fields[4])
            assert index < len(images)
            assert 0 <= x <= images[index].width - 32
            assert 0 <= y <= images[index].height - 32
            assert re.fullmatch('[0-9A-F]{32}', fields[1])
            assert re.fullmatch('[0-9A-F]{8}', fields[2])
            tiles.append((fields[1], fields[2], line.startswith('<tile>')))
        elif body.startswith('<addition>'):
            fields = body[10:].split(',')
            identity = tuple(fields[:4] + fields[6:])
            assert identity not in anchors
            anchors.add(identity)
            additions.append((tuple(fields[:2]), tuple(fields[4:6])))
    keys = {entry[:2] for entry in tiles}
    fallbacks = {entry[:2] for entry in tiles if entry[2]}
    assert all(a in keys and v in keys and v in fallbacks for a, v in additions)
    return {'runtime_images': len(images), 'tile_rules': len(tiles),
            'sprite_additions': len(additions), 'duplicate_additions': 0,
            'invalid_tiles': 0, 'virtual_fallbacks_complete': True}

def replay(pack, original, result):
    frames = 12044
    assert int((result / 'home/done').read_text()) == frames
    checkpoint_files = sorted((original / 'frames').glob('*.ram'))
    assert {int(p.stem) for p in checkpoint_files} == {1, frames} | set(range(60, frames + 1, 60))
    for p in checkpoint_files:
        for suffix in ('.ram', '.ppu'):
            assert p.with_suffix(suffix).read_bytes() == (result / 'frames' / p.with_suffix(suffix).name).read_bytes()
    for p in pack.iterdir():
        assert p.read_bytes() == (result / 'home/HdPacks/Bionic Commando (USA)' / p.name).read_bytes()
    log = (result / 'log.txt').read_text()
    assert not re.search(r'\[HDPack\].*(?:error|invalid|unable)|script error|Exception', log, re.I)
    import csv
    audit = list(csv.DictReader((result / 'home/audit.tsv').open(), delimiter='\t'))
    missing = [row for row in audit if row['rule'] == '-1']
    assert not missing, missing
    return {'movie_input_frames': frames, 'ram_checkpoints': len(checkpoint_files),
            'ppu_checkpoints': len(checkpoint_files), 'state_mismatches': 0,
            'audited_graphics_states': len(audit), 'uncovered_graphics_states': 0,
            'screenshots': len(list((result / 'frames').glob('*.png'))),
            'loaded_pack_matches_extracted_zip': True}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack', type=Path, default=ROOT / 'pack')
    parser.add_argument('--original', type=Path)
    parser.add_argument('--replay', type=Path)
    args = parser.parse_args()
    report = {'structure': structure(args.pack)}
    if args.replay:
        report['playback'] = replay(args.pack, args.original, args.replay)
    (ROOT / 'validation/v0110-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
