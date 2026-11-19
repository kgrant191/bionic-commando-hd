"""Extend the Area 8 facility doors to every observed exterior lintel and palette."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

from build_v0150 import ART, DATA, EMPTY, LANCZOS, NORMAL, tone
from build_v0152 import quadrant, tile_at

ATLAS = 'area8-doors-v0153.png'
STEEL = ('0F13020B', '0F221202', '0F201000')
COPPER = ('0F261606', '0F271606')


def faded(palette, level):
    colors = bytes.fromhex(palette)
    return ''.join(f'{c-16*level:02X}' if c >= 16*level and c not in (13,14,15) else '0F' for c in colors)


def door_art(source, lines, layouts):
    sheet = Image.open(ART/'area8-facilities-v0152.png').convert('RGBA')
    source_door = [quadrant(sheet, i).resize((128,128), LANCZOS) for i in range(2)]
    # The interior radio door has an established amber caged indicator. Take just
    # the light so that both exterior frames retain their own metals and rivets.
    imgs = [line[5:] for line in lines if line.startswith('<img>')]
    head = layouts['radio'][0]
    donor = Image.new('RGBA',(128,32))
    atlas = Image.open(source/imgs[0]).convert('RGBA')
    for x,key in enumerate(head):
        raw = next(line.split('<tile>')[1].split(',') for line in lines
                   if line.startswith('[!title&!worldmap&!equipment&!radio&!areaClear&!interception&!interception14]<tile>0,'+key+',0F301000,'))
        donor.paste(tile_at(atlas,int(raw[3]),int(raw[4])),(32*x,0))
    light = donor.crop((49,2,80,17)).resize((25,13),LANCZOS)
    images = {}
    for finish,base in zip(('steel','copper'),source_door):
        images[finish,'passage'] = base
        images[finish,'goal'] = base
        radio = base.copy()
        radio.paste(light,(52,4))
        images[finish,'radio'] = radio
    return images


class DoorRules:
    def __init__(self,index):
        self.index = index
        self.pixels = {}
        self.rules = {}
        self.conditions = {}

    def condition(self,spec):
        name = 'a853_'+hashlib.sha256(spec.encode()).hexdigest()[:14]
        self.conditions[name] = spec
        return name

    def nearby(self,dx,dy,key,pal):
        # Conditions refer to the visible PPU screen; disallow the opposite edge
        # when a doorway enters from the left, right, top, or bottom.
        guards = []
        for axis,off,limit in [('X',dx,256),('Y',dy,240)]:
            if off:
                op,bound = ('>=',-off) if off<0 else ('<',limit-off)
                guards.append(self.condition(f'positionCheck{axis},{op},{bound}'))
        guards.append(self.condition(f'tileNearby,{dx},{dy},{key},{pal},N'))
        return tuple(guards)

    def emit(self,scope,guards,key,pal,cell):
        token = cell.tobytes()
        index = self.pixels.setdefault(token,len(self.pixels))
        guard = '&'.join((scope,*dict.fromkeys(guards)))
        line = f'[{guard}]<tile>{self.index},{key},{pal},{32*(index%32)},{32*(index//32)},1,N'
        self.rules.setdefault(line,None)

    def paint(self,layout,pal,image):
        for y,row in enumerate(layout):
            for x,key in enumerate(row):
                cell=tile_at(image,32*x,32*y)
                if y==0 or (y==1 and key!=EMPTY):
                    self.emit(NORMAL,(),key,pal,cell)
                    continue
                if y==1:
                    for side in (0,3):
                        check=self.nearby(8*(side-x),0,row[side],pal)
                        self.emit(NORMAL,check,key,pal,cell)
                    continue
                # Distinguish the repeated middle and threshold rows using the
                # upper jamb, whichever side and scanlines are currently visible.
                for side in (0,3):
                    upper=self.nearby(8*(side-x),8*(1-y),layout[1][side],pal)
                    self.emit(NORMAL,upper,key,pal,cell)
        # If a lift scrolls the header and upper jamb off the top of the screen,
        # resolve the two lower rows from a surviving pillar and its continuation.
        for x,key in enumerate(layout[2]):
            for side in (0,3):
                dx=8*(side-x)
                same=self.nearby(dx,0,layout[2][side],pal)
                below=self.nearby(dx,8,layout[2][side],pal)
                self.emit(NORMAL,same+below,key,pal,tile_at(image,x*32,64))
        for x,key in enumerate(layout[3]):
            for side in (0,3):
                same=self.nearby(8*(side-x),0,layout[3][side],pal)
                self.emit(NORMAL,same,key,pal,tile_at(image,x*32,96))

    def save(self,dest):
        atlas=Image.new('RGBA',(1024,32*((len(self.pixels)+31)//32)))
        for data,index in self.pixels.items():
            atlas.paste(Image.frombytes('RGBA',(32,32),data),(32*(index%32),32*(index//32)))
        atlas.save(dest/ATLAS,optimize=True)


def build(source,dest):
    lines=(source/'hires.txt').read_text().splitlines()
    if 'v0.15.2' not in lines[0]:raise ValueError('Expected the v0.15.2 pack')
    layouts=json.loads((DATA/'doors-v0153.json').read_text())['layouts']
    images=door_art(source,lines,layouts)
    out=DoorRules(sum(s.startswith('<img>') for s in lines))
    for pal in (*STEEL,*COPPER):
        finish = 'steel' if pal in STEEL else 'copper'
        kinds=['passage']
        if pal in ('0F201000','0F271606'):kinds.append('radio')
        if pal=='0F261606':kinds.append('goal')
        for level,brightness in enumerate((1,.58,.24)):
            color=faded(pal,level)
            if len(set(bytes.fromhex(color)))==1:continue
            for kind in kinds:
                image=images[finish,kind]
                out.paint(layouts[kind],color,image if not level else tone(image,brightness))
    dest.mkdir(parents=True,exist_ok=True)
    for p in source.iterdir():
        if p.name not in ('hires.txt','README.txt'):shutil.copy2(p,dest/p.name)
    out.save(dest)
    first=next(i for i,s in enumerate(lines) if '<tile>'in s)
    lines[first:first]=[f'<img>{ATLAS}',*[f'<condition>{n},{v}' for n,v in out.conditions.items()],*out.rules]
    lines[0]='# Bionic Commando HD v0.15.3 - Area 8 facility doors'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    note=(source/'README.txt').read_text().replace('v0.15.2','v0.15.3',1)
    note=note.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nCompleted the steel and copper doorways on the towers and lifts, including the exterior radio-room entrances.\n\nPREVIOUS BUILDS\n',1)
    (dest/'README.txt').write_text(note)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('dest',type=Path)
    args=ap.parse_args()
    build(args.source,args.dest)
