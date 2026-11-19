"""Build an Area 8 fallback-probe pack for a MesenCE regression replay.

Each low-priority diagnostic mapping draws a unique two-colour signature on
the opaque native pixels only. All ordinary HD mappings keep their priority.
The renderer-side fallback_probe.cpp records these signatures and frame numbers.
"""
import argparse
import gzip
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

CATALOGUE = Path(__file__).resolve().parents[1] / 'capture/area8/fallback-catalogue.json.gz'


def make_probe(pack, dest):
    if dest.resolve()==pack.resolve():
        raise ValueError('Choose a separate directory for the diagnostic pack')
    keys=json.loads(gzip.decompress(CATALOGUE.read_bytes()))
    lines=(pack/'hires.txt').read_text().splitlines()
    sheet_id=sum(line.startswith('<img>') for line in lines)
    atlas=Image.new('RGBA',(2048,32*((len(keys)+63)//64)))
    for i,(key,palette) in enumerate(keys):
        mask=np.unpackbits(np.frombuffer(bytes.fromhex(key),dtype=np.uint8)).reshape(16,8)
        cell=np.zeros((32,32,4),np.uint8)
        cell[:,:,:3]=(255,(i>>8)+2,i%256)
        cell[:,3::4,:3]=(5,241,158)
        cell[:,:,3]=(mask[:8]|mask[8:]).repeat(4,axis=0).repeat(4,axis=1)*255
        left,top=i%64*32,i//64*32
        atlas.paste(Image.fromarray(cell),(left,top))
        lines.append(f'[area8]<tile>{sheet_id},{key},{palette},{left},{top},1,N')
    first=next(i for i,line in enumerate(lines) if '<tile>' in line)
    lines.insert(first,'<img>expanded.png')
    dest.mkdir(parents=True,exist_ok=True)
    for f in pack.iterdir():
        if f.is_file() and f.name!='hires.txt':
            shutil.copyfile(f,dest/f.name)
    atlas.save(dest/'expanded.png')
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    print(f'{len(keys)} tile and palette combinations')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack',type=Path)
    parser.add_argument('dest',type=Path)
    args=parser.parse_args()
    make_probe(args.pack,args.dest)
