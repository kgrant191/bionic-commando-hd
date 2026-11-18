"""Area 2 blue slime material and native two-step rifleman animation."""
from pathlib import Path
import argparse
import json
import shutil
from build_v0112 import build as previous_build

ROOT = Path(__file__).resolve().parents[1]


def build(dest):
    previous_build(dest, enemy_records=ROOT/'capture/area2-v0113/enemy-poses.json',
                   slime_sheet=ROOT/'art/area2-blue-slime-v0113.png')
    for name in ['area2-v0110', 'area2-polish-v0112']:
        target = 'area2-actors-v0113' if name == 'area2-v0110' else 'area2-slime-v0113'
        (dest/(name+'.png')).replace(dest/(target+'.png'))
        p=dest/'hires.txt';p.write_text(p.read_text().replace('<img>'+name+'.png', '<img>'+target+'.png'))
    p=dest/'hires.txt';lines=p.read_text().splitlines()
    lines[0]='# Bionic Commando HD v0.11.3 - blue slime and rifleman walking frames'
    p.write_text('\n'.join(lines)+'\n')
    p=dest/'README.txt';text=p.read_text().replace('v0.11.2','v0.11.3')
    text=text.replace('NEW IN THIS BUILD\n', 'NEW IN THIS BUILD\nThick blue slime pools, pipe discharge and moving blob phases in Area 2.\nThe short red rifleman uses distinct native-timed walking poses.\nIncludes the opaque doorway and screen-boundary crash fix.\n\n')
    text=text.replace('water-splash phases','slime-blob phases').replace('animated water and','blue slime and')
    p.write_text(text)
    report={name:json.loads((ROOT/'validation'/filename).read_text()) for name,filename in
            [('actors','v0110-build.json'),('slime_atlas','v0111-build.json'),('bounds','v0112-build.json')]}
    report['version']='0.11.3'
    report['fluid_scope']='Area 2; native blue background/sprite palette pairs only.'
    (ROOT/'validation/v0113-build.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copy2(ROOT/'validation/v0110-enemy-poses.json',ROOT/'validation/v0113-enemy-poses.json')
    preview=ROOT/'validation/pose-previews/area2-v0113';preview.mkdir(exist_ok=True,parents=True)
    for n in [18,19]:shutil.copy2(ROOT/f'validation/pose-previews/area2/{n}.png',preview/f'{n}.png')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'pack')
    build(parser.parse_args().output)


if __name__=='__main__':main()
