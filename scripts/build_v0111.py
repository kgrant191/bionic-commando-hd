"""Area 2 visual corrections from the nine v0.11.0 review screenshots."""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, json, re, shutil, tempfile
import numpy as np
from PIL import Image, ImageOps
from build_v0110 import build as previous_build, NORMAL
from poses import make_actor

ROOT = Path(__file__).resolve().parents[1]
CAVE = NORMAL + '&a2Cave'
OUTSIDE = NORMAL + '&a2Outside'

def entries(n):
    return [(int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6]))
            for a in (line.split(',') for line in
            (ROOT/f'capture/area2-polish/{n:05}.tiles').read_text().splitlines())]

def cell(sheet, n, cols=3, rows=2, main_component=False):
    w,h=sheet.width//cols,sheet.height//rows
    im=sheet.crop((n%cols*w,n//cols*h,(n%cols+1)*w,(n//cols+1)*h))
    # Generated assets have genuine alpha; remove only faint gutter residue.
    a=np.array(im);a[a[:,:,3]<32,3]=0;im=Image.fromarray(a)
    solid=np.array(im.getchannel('A'))>64
    if main_component:
        from scipy.ndimage import label,find_objects
        labels,count=label(solid)
        sizes=np.bincount(labels.ravel());sizes[0]=0
        yy,xx=find_objects((labels==sizes.argmax()).astype(np.uint8))[0]
        box=(xx.start,yy.start,xx.stop,yy.stop)
    else:box=im.getchannel('A').point(lambda a:255 if a>64 else 0).getbbox()
    return im.crop(box)

def fit(im, size):
    return im.resize(size,Image.Resampling.LANCZOS)

def build(dest, door_backing=None):
    previous_build(dest)
    lines=(dest/'hires.txt').read_text().splitlines()
    images=[Image.open(dest/l[5:]).convert('RGBA') for l in lines if l.startswith('<img>')]
    index=len(images);atlas=Image.new('RGBA',(2048,4096));cells={};rules=[];conds=[];adds=[]
    blank=Image.new('RGBA',(32,32));nearby={}
    audit=json.loads((ROOT/'capture/area2/audit-before.json').read_text())
    pairs={(r['key'],int(r['palette'],16)) for r in audit}
    keyp=defaultdict(set);by=defaultdict(list)
    for k,p in pairs:keyp[k].add(p)
    for l in lines:
        if '<tile>' in l:
            g,b=l.split('<tile>');a=b.split(',');by[a[1],int(a[2],16)].append((g,a))

    def emit(k,p,im,g=NORMAL):
        assert im.size==(32,32),im.size
        data=im.tobytes()
        if data not in cells:
            n=len(cells);xy=n%64*32,n//64*32;assert xy[1]<4096
            cells[data]=xy;atlas.paste(im,xy)
        x,y=cells[data]
        rules.append((f'[{g}]' if g else '')+f'<tile>{index},{k},{p:08X},{x},{y},1,N')

    def near(kind,x,y,k,p,ignore=False):
        t=kind,x,y,k,p,ignore
        if t not in nearby:
            name=f'a211Near{len(nearby)}';nearby[t]=name
            conds.append(f'<condition>{name},{kind}Nearby,{x},{y},{k},{p:08X},{"Y" if ignore else "N"}')
        return nearby[t]

    def piece(im,x,y):return im.crop((x*4,y*4,(x+8)*4,(y+8)*4))
    sheet=Image.open(ROOT/'art/area2-structures-v0111.png').convert('RGBA')
    art=[cell(sheet,n,main_component=True) for n in range(6)]

    # Whole facade slices are selected by nearby unique architectural anchors.
    # Repeated native plaster/roof cells can consequently carry different art.
    es=[e for e in entries(720) if e[0]==0 and 64<=e[1]<160 and 112<=e[2]<192]
    facade=fit(art[0],(384,320));counts=Counter((e[3],e[4]) for e in es)
    if door_backing is not None:
        # The opening is a dark interior, not a window into the sky layer.
        backing=Image.new('RGBA',facade.size)
        backing.paste(fit(Image.open(door_backing).convert('RGBA'),(86,156)),(150,164))
        backing.alpha_composite(facade)
        facade=backing
    anchors=[e for e in es if counts[e[3],e[4]]==1]
    for _,x,y,k,p,h,v in es:
        im=piece(facade,x-64,y-112)
        if counts[k,p]==1:emit(k,p,im,OUTSIDE)
        else:
            for _,ax,ay,ak,ap,_,_ in sorted(anchors,key=lambda e:abs(e[1]-x)+abs(e[2]-y))[:3]:
                emit(k,p,im,OUTSIDE+'&'+near('tile',ax-x,ay-y,ak,ap))

    # Modular header and continuous jambs keep native open doorway dimensions.
    door=fit(art[1],(128,192))
    header=fit(art[1].crop((0,0,art[1].width,round(art[1].height*.25))),(128,32))
    door.paste(header,(0,0))
    for n,box in [(1170,(32,80,64,128)),(3150,(20,45,52,93))]:
        x0,y0,x1,y1=box;done=set()
        for ly,x,y,k,p,h,v in entries(n):
            if ly!=0 or not(x0<=x<x1 and y0<=y<y1) or k=='0'*32 or k in done:continue
            done.add(k);yy=y-y0
            # Repeated jamb cells must have the same texture at each seam.
            if yy>=16:yy=64//4
            emit(k,p,piece(door,x-x0,yy),CAVE)

    # Supply crates retain their native two-by-two cell footprints.
    crate=fit(art[4],(64,64))
    for ly,x,y,k,p,h,v in entries(3150):
        if ly==0 and 52<=x<68 and 77<=y<93:
            emit(k,p,piece(crate,x-52,y-77),CAVE)

    # Steel drain outlet, separate from the animated water below its mouth.
    outlet=fit(art[3],(64,128))
    for ly,x,y,k,p,h,v in entries(1170):
        if ly==0 and 80<=x<96 and 80<=y<112:
            emit(k,p,piece(outlet,x-80,y-80),CAVE)

    # CHR shapes used as rock elsewhere are water in this palette. Classify
    # by the complete pattern/palette pair, avoiding stone patches in streams.
    materials=Image.open(ROOT/'art/area2-materials-v0110.png').convert('RGBA')
    flow=fit(materials.crop((materials.width//2,materials.height//2,materials.width,materials.height)),(128,128))
    water_ids={8,9,16,17,26,27,28,29,30,31,32,33,37,41,71,72,73,74,99,103}
    for e in json.loads((ROOT/'capture/area2/material-catalog.json').read_text()):
        if e['layer']==0 and e['palette']=='0F2B1C0B' and e['index'] in water_ids:
            phase=e['index']%4
            emit(e['key'],0x0F2B1C0B,flow.crop((phase*32,32,phase*32+32,64)),CAVE)

    catalog=json.loads((ROOT/'capture/area2/material-catalog.json').read_text())
    bgids={e['index']:e['key'] for e in catalog if e['layer']==0 and e['palette']=='0F2B1C0B'}
    def old_crop(k,p):
        g,a=by[k,p][0];x,y=map(int,a[3:5])
        return images[int(a[0])].crop((x,y,x+32,y+32))
    bricks=old_crop(bgids[0],0x0F2B1C0B)
    for i in [78,79]:
        bits=np.unpackbits(np.frombuffer(bytes.fromhex(bgids[i]),dtype=np.uint8)).reshape(16,8)
        mask=np.repeat(np.repeat((bits[:8]+2*bits[8:])>0,4,0),4,1)
        im=bricks.copy();im.putalpha(Image.fromarray(mask.astype('uint8')*255))
        emit(bgids[i],0x0F2B1C0B,im,CAVE)

    # One connected pipe assembly spans the native decorative panel. Nearby
    # anchors disambiguate repeated wall/empty cells and survive scrolling.
    pa=fit(art[2],(384,320))
    # The later shaft uses a narrow capped pipe, with different upper/lower
    # native patterns. Keep its shared middle cells separate from the wide U.
    narrow=Image.new('RGBA',(128,256))
    narrow.alpha_composite(fit(pa.crop((0,60,136,320)),(64,224)),(64,32))
    narrow.alpha_composite(fit(pa.crop((0,60,136,170)),(48,72)),(8,32))
    narrow.alpha_composite(fit(art[1].crop((0,0,art[1].width,round(art[1].height*.25))),(128,32)))
    narrow_es=[e for e in entries(7693) if e[0]==0 and e[4]==0x0F2B1C0B
               and 43<=e[1]<75 and 130<=e[2]<194]
    nc=Counter(e[3] for e in narrow_es)
    na=[e for e in narrow_es if nc[e[3]]==1 and e[3] in {bgids[i] for i in range(109,125)}]
    for _,x,y,k,p,h,v in narrow_es:
        under=bricks.copy();under.alpha_composite(piece(narrow,x-43,y-130))
        for _,ax,ay,ak,ap,_,_ in sorted(na,key=lambda e:abs(e[1]-x)+abs(e[2]-y))[:3]:
            emit(k,p,under,CAVE+'&'+near('tile',ax-x,ay-y,ak,ap))
    pipe_es=[e for e in entries(6810) if e[0]==0 and e[4]==0x0F2B1C0B
             and 8<=e[1]<104 and 82<=e[2]<162]
    counts=Counter((e[3],e[4]) for e in pipe_es)
    anchors=[e for e in pipe_es if counts[e[3],e[4]]==1]
    ordinary={bgids[i] for i in [0,1,2,3,4,5,6,7,10,11,12,78,79]}
    for _,x,y,k,p,h,v in pipe_es:
        if k in ordinary:under=old_crop(k,p)
        else:under=bricks.copy()
        under.alpha_composite(piece(pa,x-8,y-82))
        if counts[k,p]==1 and k not in ordinary:emit(k,p,under,CAVE)
        else:
            for _,ax,ay,ak,ap,_,_ in sorted(anchors,key=lambda e:abs(e[1]-x)+abs(e[2]-y))[:3]:
                emit(k,p,under,CAVE+'&'+near('tile',ax-x,ay-y,ak,ap))

    # Wall grilles use the painted vent and frame material from the doorway.
    grille=fit(art[1].crop((0,0,art[1].width,round(art[1].height*.25))),(128,64))
    for ly,x,y,k,p,h,v in entries(6810):
        if ly==0 and p==0x0F2B1C0B and 136<=x<168 and 146<=y<162:
            emit(k,p,piece(grille,x-136,y-146),CAVE)

    # The old repeated pale gear motif is a compact paired ledge mounting.
    bracket=fit(art[5],(64,64));catalog=json.loads((ROOT/'capture/area2/material-catalog.json').read_text())
    ids={e['index']:e['key'] for e in catalog if e['layer']==0 and e['palette']=='0F281808'}
    for i,x,y in [(12,0,0),(13,8,0),(14,0,8),(15,8,8)]:
        for p in sorted(keyp[ids[i]]):
            if p>>24!=255:emit(ids[i],p,piece(bracket,x,y),CAVE)

    # Native explosion phases, including grenades, retain their OAM footprint.
    fx=Image.open(ROOT/'art/area2-effects-v0111.png').convert('RGBA')
    explosion_keys=set()
    for n,c in [(833,0),(838,1),(843,2)]:
        selected=[e for e in entries(n) if e[0]==1 and e[4]==0xFF30160F and 50<e[1]<115 and e[2]>=150]
        x0=min(e[1] for e in selected);y0=min(e[2] for e in selected)
        w=max(e[1] for e in selected)+8-x0;h=max(e[2] for e in selected)+8-y0
        effect=fit(cell(fx,c),(w*4,h*4));seen=set()
        for _,x,y,k,p,hm,vm in selected:
            if k in seen:continue
            seen.add(k);explosion_keys.add(k);im=piece(effect,x-x0,y-y0)
            if hm:im=ImageOps.mirror(im)
            if vm:im=ImageOps.flip(im)
            for pp in keyp[k]:
                if pp>>24==255:emit(k,pp,im)

    # Water's native rise/fall shapes are independently selected by neighbor
    # patterns, so a taller plume never stretches a short splash's cells.
    waterkeys=set();waterseen=set();waterfallback={}
    water_records=json.loads((ROOT/'capture/area2-polish/water-assemblies.json').read_text())
    for rec in sorted(water_records,key=lambda r:(-len(r['parts']),-r['count'])):
        selected=rec['parts'];w=max(e[0] for e in selected)+8;h=max(e[1] for e in selected)+8
        phase=3 if h<=8 else 4 if h>=24 else 5
        effect=fit(cell(fx,phase),(max(16,w)*4,h*4))
        if w==8:
            right=bool(selected[0][3]);effect=effect.crop((32 if right else 0,0,64 if right else 32,h*4))
        for x,y,k,hm,vm in selected:
            p=0xFF302C0F;im=piece(effect,x,y)
            if hm:im=ImageOps.mirror(im)
            if vm:im=ImageOps.flip(im)
            tests=['hmirror' if hm else '!hmirror','vmirror' if vm else '!vmirror']
            for xx,yy,kk,hh,vv in selected:
                if (xx,yy)!=(x,y):tests.append(near('sprite',(xx-x)*(-1 if hm else 1),(yy-y)*(-1 if vm else 1),kk,p))
            g=NORMAL+'&'+'&'.join(tests);sig=k,p,g
            if sig not in waterseen:emit(k,p,im,g);waterseen.add(sig)
            waterkeys.add(k);waterfallback.setdefault((k,p),im)
    for (k,p),im in waterfallback.items():emit(k,p,im,NORMAL)

    # Complete painted hurt/recoil actor, including every observed flash palette.
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        for folder in ['capture','art','validation']:(tmp/folder).mkdir()
        shutil.copy2(ROOT/'capture/area2-polish/recoil-poses.json',tmp/'capture/enemy-poses.json')
        shutil.copy2(ROOT/'capture/spencer-poses.json',tmp/'capture/spencer-poses.json')
        for p in (ROOT/'art').glob('*.png'):(tmp/'art'/p.name).symlink_to(p)
        pending=[]
        c,a,v=make_actor(tmp,pairs,lambda k,p,im,g=None:pending.append((k,p,im,g)),blank,'enemy',1,0xFF36150F)
        names={l.split(',')[0][11:]:'a211_'+l.split(',')[0][11:] for l in c}
        def rename(s):return re.sub(r'[A-Za-z_][A-Za-z0-9_-]*',lambda m:names.get(m.group(),m.group()),s)
        conds.extend(map(rename,c));adds.extend(a)
        for k,p,im,g in pending:emit(k,p,im,NORMAL+('&'+rename(g) if g else ''))
        for k,p in v:emit(k,p,blank,None)
        shutil.copy2(tmp/'validation/enemy_pose_mapping.json',ROOT/'validation/v0111-recoil.json')
        preview=ROOT/'validation/pose-previews/area2-polish';preview.mkdir(parents=True,exist_ok=True)
        shutil.copy2(tmp/'validation/pose-previews/enemy/200.png',preview/'recoil.png')

    # The damage cycle can give Spencer's anchor a previously unseen aqua
    # palette. Clone his complete existing weapon/pose assembly, not just
    # recolored native body cells. New palette additions are Area 2 blank
    # outside the scoped overrides.
    heads={r.get('head','000102F17A797A7E52FFFE8F7E67064E') for r in json.loads((ROOT/'capture/spencer-poses.json').read_text())}
    existing={tuple(l[10:].split(',')[:4]) for l in lines if l.startswith('<addition>')}
    aliased=set()
    for l in lines:
        if not l.startswith('<addition>'):continue
        a=l[10:].split(',');k,p=a[0],int(a[1],16)
        if k not in heads or p!=0xFF36060F:continue
        for pp in keyp[k]:
            if (k,f'{pp:08X}',a[2],a[3]) in existing:continue
            aa=a.copy();aa[1]=aa[5]=f'{pp:08X}';adds.append('<addition>'+','.join(aa));aliased.add((a[4],pp))
            for g,b in by[a[4],p]:
                x,y=map(int,b[3:5]);im=images[int(b[0])].crop((x,y,x+32,y+32))
                emit(a[4],pp,im,NORMAL+('&'+g[1:-1] if g else ''))
            emit(a[4],pp,blank,None)

    # Keep source declaration order stable, with the scoped replacements first.
    at=next(i for i,l in enumerate(lines) if '<tile>' in l)
    lines[at:at]=['<img>area2-polish-v0111.png']+conds+adds+list(dict.fromkeys(rules))
    lines[0]='# Bionic Commando HD v0.11.1 - Area 2 visual corrections'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0,0,2048,max(32,((len(cells)+63)//64)*32))).save(dest/'area2-polish-v0111.png')
    readme=(dest/'README.txt').read_text().replace('v0.11.0','v0.11.1')
    readme=readme.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nRepainted outpost, doorway frames, pipes, outlets, crates and ledge mounts.\nNew grenade explosion and water-splash phases. Painted red recoil poses\nand complete Spencer damage-palette assembly. Area 2 playback only.\n\n')
    (dest/'README.txt').write_text(readme)
    report={'version':'0.11.1','new_art_cells':len(cells),'rules':len(set(rules)),
            'new_additions':len(adds),'spencer_palette_cells':len(aliased),
            'explosion_patterns':len(explosion_keys),'water_patterns':len(waterkeys)}
    (ROOT/'validation/v0111-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'pack');build(ap.parse_args().output)

if __name__=='__main__':main()
