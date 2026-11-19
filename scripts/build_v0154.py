"""Render Area 8's airborne soldiers from their live object slots and restore the goal insignia."""
import argparse
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from build_v0150 import ART, NORMAL, cropped, recolor_cloth
from build_v0153 import faded

HEAD_BLUE='000201077C3C3C3F003E7F7F7F07372F'
HEAD_RED='00020101717F3E3F003E7F7F7F3F0A1F'
CANOPY=('00000000031F3F7F0000000002091224','7F44FFFFFDFC7E7E24FF44EEB5B45A5A','FCFCF8F8F0E0E0E0D4B4A8A8F0202020')
TORSO_BLUE=('00001EBFBFC1C1E300001EAFBFFFFFFF','13060606033F07131F3F3F3F3F3C1C1E','7F313179FDFDFFFCFFFFDF8F87E7070C')
TORSO_RED=('0020FF0107FF070300E0FFFFFDFC0403','3C18FE8387FFDFFF77FFFFFFFF7178F8','40202071F9FFFFF3C0E0E09F1F8F0F13')
LEGS=('0F010100380F040C0F0F1F3F3F7FFFFF','3030E80808F02020F0F0F8F8F8F0E0E0','128A71787878F8F8F3FB7178787878F8','601018FC7E1E1E3CE0F0F8FC7E1E0E3C','00000000000001030000000000000103')
EAGLE=('FBF478FDFBC2F2F50AFD85FEE6C3F3CD','DF2F5EBEDC414DBC10BFE17E64C1CDA0')
SLOTS=(8,9,10)

def artwork(dest):
    original=cropped(Image.open(ART/'area8-approved-paratrooper.png').convert('RGBA'))
    blue=original.copy()
    # Preserve the red recognition stripe and dye only the uniform underneath it.
    seam=int(.53*original.height)
    blue.paste(recolor_cloth(original.crop((0,seam,original.width,original.height))),(0,seam))
    # Orange edge highlights on the original burgundy trousers belong to the cloth.
    # Dye those highlights as well while keeping the hands, face and leather intact.
    a=np.array(blue);raw=np.array(original);r,g,b=raw[:,:,:3].astype(float).transpose(2,0,1)
    yy=np.indices(r.shape)[0]/original.height
    cloth=(yy>.775)&(yy<.91)&(r>1.30*g)&(r>1.50*b)
    lum=r*.70+g*.20+b*.10
    for ch,scale,base in [(0,.50,4),(1,.82,7),(2,1.10,15)]:
        a[:,:,ch][cloth]=np.clip(lum[cloth]*scale+base,0,255)
    blue=Image.fromarray(a)
    names={}
    for color,art in [('r',original),('b',blue)]:
        art=art.resize((round(art.width*208/art.height),208),Image.Resampling.LANCZOS)
        art.putalpha(art.getchannel('A').point(lambda a:255 if a>=247 else 0 if a<8 else a))
        for face in (0,1):
            name=f'area8-chute-{color}{face}-v0154.png'
            plate=Image.new('RGBA',(1200,1220))
            pic=ImageOps.mirror(art) if not face else art
            plate.alpha_composite(pic,(1024-pic.width//2,1024+64-pic.height))
            plate.save(dest/name,optimize=True);names[color,face]=name
    return names

def build(source,dest):
    dest.mkdir(exist_ok=True,parents=True)
    lines=(source/'hires.txt').read_text().splitlines()
    assert 'v0.15.3' in lines[0]
    for f in source.iterdir():
        if f.name not in ('hires.txt','README.txt'):shutil.copyfile(f,dest/f.name)
    sheets=[q[5:]for q in lines if q.startswith('<img>')]
    eagle=sheets.index('boss-door-eagle-v0115.png')
    rules=[]; cond={}
    def condition(spec):
        if spec not in cond:cond[spec]='p54'+str(len(cond))
        return cond[spec]
    def reg(addr,n,mask=255):
        return condition(f'memoryCheckConstant,{addr:04X},==,{n:02X},{mask:02X}')
    def bound(axis,lo,hi):
        tests=[]
        if lo>0:tests.append(condition(f'originPositionCheck{axis},>=,{lo}'))
        if hi<255:tests.append(condition(f'originPositionCheck{axis},<=,{hi}'))
        return tests
    for j,k in enumerate(EAGLE):
        for level,bright in enumerate((1,.58,.24)):
            rules.append(f'[{NORMAL}]<tile>{eagle},{k},{faded("0F261606",level)},{32*j},0,{bright},N')
    names=artwork(dest)
    
    enable=condition('ppuMemoryCheckConstant,3F1D,==,30')
    pieces={}
    def piece(key,pal,offset):
        pieces.setdefault((key,pal),set()).add(offset)
    # Relative position of the original 8x8 body pieces in native screen pixels.
    for head,torso,colors in [(HEAD_BLUE,TORSO_BLUE,('FF30210F',)),(HEAD_RED,TORSO_RED,('FF36150F','FF36160F','FF30160F','FF30150F','FF30210F'))]:
        for pal in colors:
            piece(head,pal,(0,-16))
            for j,k in enumerate(torso):piece(k,pal,(0,-16 if head==HEAD_BLUE and j==0 else -8))
            for j,k in enumerate(LEGS):piece(k,pal,(0,0 if j<2 else 8))
    physical=dict(pieces)
    canopy_keys=set()
    for k in CANOPY:
        for pal in ('FF30210F','FF30150F','FF30160F'):canopy_keys.add((k,pal))
    for line in lines:
        if not line.startswith('<addition>'):continue
        key,pal,x,y,v,vc,_=line[10:].split(',')
        if (key,pal) in physical:
            for _,dy in physical[key,pal]:piece(v,vc,(abs(int(x)),dy+int(y)))
        if (key,pal) in canopy_keys:canopy_keys.add((v,vc))
    clear='6,{},{},96,0,1,N'
    for k,pal in sorted(canopy_keys):
        rules.append(f'[{NORMAL}]<tile>'+clear.format(k,pal))
    # Retire the head-owned seated fallback. The on-foot actor can now select its
    # established standing/throwing artwork even when only its helmet survives.
    gold=NORMAL+'&a8BgA22&a8BgB37'
    owned={q[10:].split(',')[4] for q in lines if q.startswith('<addition>'+HEAD_BLUE+',FF30210F,')}
    def obsolete(q):
        if not q.startswith('['+gold) or '<tile>' not in q:return False
        fields=q.split('<tile>',1)[1].split(',')
        return fields[0]==str(sheets.index('area8-review-v0152.png')) and fields[1] in owned and fields[2]=='FF30210F'
    lines=[q for q in lines if not obsolete(q)]
    # Cache conditions by body-piece offsets. Hide only the native pieces near
    # that individual descending object, including partial OAM lists.
    for slot in SLOTS:
        active=reg(0x536+slot,1); air=reg(0x5e4+slot,0x90,0xDD)
        # The two actual parachute pose indices are 92 (rifle) and B0 (grenadier).
        # These two exclusions keep other animation indices out of the shared mask.
        exact=[air,'!'+reg(0x5e4+slot,0x90),'!'+reg(0x5e4+slot,0xB2)]
        valid=[active,air,reg(0x55c+slot,0),reg(0x596+slot,0),'area8']
        for x in range(0,256,32):
            cx=reg(0x56f+slot,x,224)
            for y in range(0,256,16):
                cy=reg(0x5a9+slot,y,240)
                for (k,pal),offs in pieces.items():
                    pad=max(v[0] for v in offs)
                    y0=min(v[1] for v in offs);y1=max(v[1] for v in offs)
                    if y+15+y1+8<0 or y+y0-8>239:continue
                    xs=bound('X',x-17-pad,x+31+10+pad)
                    ys=bound('Y',y+y0-8,y+15+y1+8)
                    guard='&'.join([air,cx,cy,*xs,*ys,active,'area8',*exact[1:]])
                    rules.append(f'[{guard}]<tile>'+clear.format(k,pal))
        # One compositing layer per game slot keeps simultaneous drops independent.
        # Place the complete figure as a single image. Its boots meet the floor at Y+16.
        for x in range(0,256,4):
            cx=reg(0x56f+slot,x,252)
            for y in range(0,256,2):
                cy=reg(0x5a9+slot,y,254)
                for c in ('b','r'):
                    for f in (0,1):
                        face=reg(0x633+slot,f,1)
                        pose=reg(0x5e4+slot,0xB0 if c=='b' else 0x92)
                        g='&'.join([pose,cx,cy,active,*valid[2:],enable,face,'screenEnabled'])
                        rules.append(f'[{g}]<background>{names[c,f]},1,0,0,{20+slot-8},{256-x},{256-y}')
    at=next(i for i,s in enumerate(lines)if '<tile>'in s)
    lines[at:at]=[*(f'<condition>{n},{spec}'for spec,n in cond.items()),*rules]
    lines[0]='# Bionic Commando HD v0.15.4 - Area 8 paratroopers and boss entrance'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    note=(source/'README.txt').read_text().replace('v0.15.3','v0.15.4',1)
    note=note.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nArea 8 paratroopers use the established canopy and full soldier artwork throughout descent. The final reactor entrance carries the brass eagle.\n\nPREVIOUS BUILDS\n',1)
    (dest/'README.txt').write_text(note)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('dest',type=Path)
    args=parser.parse_args();build(args.source,args.dest)
