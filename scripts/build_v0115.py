"""Identify generator/final-boss entrances with the native eagle header."""
from pathlib import Path
import argparse
import json
from PIL import Image
from build_v0114 import build as previous_build

ROOT = Path(__file__).resolve().parents[1]
# The bird's two detailed CHR cells are exclusive to the goal header. The
# radio's arrows and the shared one-pixel cells below the bird are untouched.
EAGLE_KEYS = ('FBF478FDFBC2F2F50AFD85FEE6C3F3CD',
              'DF2F5EBEDC414DBC10BFE17E64C1CDA0')
NORMAL = '!title&!worldmap&!equipment&!radio&!areaClear&!interception&!interception14'


def build(dest):
    previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    index = sum(line.startswith('<img>') for line in lines)
    palettes = {key: set() for key in EAGLE_KEYS}
    for line in lines:
        if '<tile>' not in line:
            continue
        fields = line.split('<tile>')[1].split(',')
        if fields[1] in palettes and fields[2].startswith('0F'):
            palettes[fields[1]].add(fields[2])
    assert palettes[EAGLE_KEYS[0]] == palettes[EAGLE_KEYS[1]]
    source = Image.open(ROOT/'art/boss-door-eagle-v0115.png').convert('RGBA')
    box = source.getchannel('A').point(lambda a: 255 if a > 32 else 0).getbbox()
    plaque = source.crop(box).resize((64, 32), Image.Resampling.LANCZOS)
    plaque.save(dest/'boss-door-eagle-v0115.png')
    rules = [f'[{NORMAL}]<tile>{index},{key},{palette},{col*32},0,1,N'
             for col, key in enumerate(EAGLE_KEYS) for palette in sorted(palettes[key])]
    at = next(i for i, line in enumerate(lines) if '<tile>' in line)
    lines[at:at] = ['<img>boss-door-eagle-v0115.png'] + rules
    lines[0] = '# Bionic Commando HD v0.11.5 - eagle markers on generator and boss entrances'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    readme = (dest/'README.txt').read_text().replace('v0.11.4', 'v0.11.5')
    readme = readme.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nEagle emblems distinguish generator/final-boss entrances from radio rooms.\nAll currently mapped native eagle-header palettes share the same marker.\n\n', 1)
    (dest/'README.txt').write_text(readme)
    report = {'version': '0.11.5', 'rules': len(rules), 'native_keys': EAGLE_KEYS,
              'palettes': sorted(palettes[EAGLE_KEYS[0]]), 'native_footprint': [16, 8],
              'selection': 'Native eagle header only, across existing area/palette variants',
              'new_neighbor_conditions': 0, 'ordinary_and_radio_headers_changed': False}
    (ROOT/'validation/v0115-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'pack')
    build(parser.parse_args().output)


if __name__ == '__main__':
    main()
