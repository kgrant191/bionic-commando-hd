"""Correct Area 8 sprite ownership, transient palette states, fonts and spike beds."""
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFilter

from build_v0150 import ART, DATA, ROOT, NORMAL, CLEAR, LANCZOS, Pack, bits, cropped, recolor_cloth, split, terrain

ATLAS = 'area8-regression-v0151.png'
BLUE = 'FF30210F'
RED = 'FF36150F'
GOLD = NORMAL + '&a8BgA22&a8BgB37'
CORE = NORMAL + '&a8Core'
CABLE = NORMAL + '&a8Room39'
ORIGIN = (160, 96)


class Revision(Pack):
    def __init__(self, source):
        self.lines = (source / 'hires.txt').read_text().splitlines()
        assert 'v0.15.0' in self.lines[0]
        self.sheets = [Image.open(source / s[5:]).convert('RGBA') for s in self.lines if s.startswith('<img>')]
        self.idx = len(self.sheets)
        self.cells, self.tiles, self.conditions = {}, [], {}
        self.fallbacks, self.new_add = [], []
        self.bykey, self.old_conditions, self.adds = defaultdict(list), {}, {}
        for line in self.lines:
            if '<tile>' in line:
                guards, fields = split(line, '<tile>')
                self.bykey[fields[1]].append((guards, fields))
            elif line.startswith('<condition>'):
                key, rule = line[11:].split(',', 1)
                self.old_conditions[key] = rule
            elif line.startswith('<addition>'):
                key, pal, x, y, virtual, color, _ = line[10:].split(',')
                self.adds[key, pal, int(x), int(y)] = virtual, color

    def condition(self, name, rule):
        if name in self.old_conditions:
            assert self.old_conditions[name] == rule
            return name
        return super().condition(name, rule)

    def adjacent(self, x, y, key):
        # Ignore palette for a neighboring body part. Damage and sprite multiplexing
        # can change the actor's palette between scanlines or independently of its head.
        rule = f'spriteNearby,{x},{y},{key},FF30210F,Y'
        name = self.condition('a851N' + hashlib.sha1(rule.encode()).hexdigest()[:12], rule)
        if y:
            edge = 240-y if y>0 else -y
            cmp = '<' if y>0 else '>='
            bound = self.condition('a851'+('Lt' if y>0 else 'Ge')+str(edge),f'positionCheckY,{cmp},{edge}')
            return bound+'&'+name
        return name

    def save(self, source, dest):
        dest.mkdir(parents=True,exist_ok=True)
        for f in source.iterdir():
            if f.name not in ('hires.txt','README.txt'):
                shutil.copy2(f,dest/f.name)
        sheet=Image.new('RGBA',(1280,32*((len(self.cells)+39)//40)))
        for pixels,i in self.cells.items():
            sheet.paste(Image.frombytes('RGBA',(32,32),pixels),(i%40*32,i//40*32))
        sheet.save(dest/ATLAS,optimize=True)
        at=next(i for i,l in enumerate(self.lines) if '<tile>' in l)
        self.lines[at:at]=[f'<img>{ATLAS}',*[f'<condition>{n},{r}'for n,r in self.conditions.items()],
                          *dict.fromkeys(self.tiles),*dict.fromkeys(self.fallbacks)]
        self.lines.extend(self.new_add)
        self.lines[0]='# Bionic Commando HD v0.15.1 - Area 8 regression'
        (dest/'hires.txt').write_text('\n'.join(self.lines)+'\n')
        text=(source/'README.txt').read_text().replace('v0.15.0','v0.15.1',1)
        text=text.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nConsistent spike blades and shafts, painted enemy damage and clipped poses,\nrail-gun effects, radio text and the Area 8 clear numeral.\n\nPREVIOUS BUILDS\n',1)
        (dest/'README.txt').write_text(text)


def light(im, amount):
    rgb=ImageEnhance.Brightness(im.convert('RGB')).enhance(amount).convert('RGBA')
    rgb.putalpha(im.getchannel('A'))
    return rgb


def spikes(p, modules):
    source=cropped(Image.open(ART/'area8-spike-v0151.png').convert('RGBA'))
    block=Image.new('RGBA',(64,128))
    # Each 16x32 NES repeat has two high tips and a shorter, overlapping front tip.
    # Every point terminates in a shaft of the same steel, down to the floor.
    for x,y,w,h in [(29,5,20,123),(3,0,23,128),(46,64,18,64)]:
        block.alpha_composite(source.resize((w,h),LANCZOS),(x,y))
    keys=[q[0] for i in ('38','56') for q in modules['tower'][i]]
    for palette, tint in [('0F3A2A1A',(0.87,1.04,.92)),('0F372717',(1.09,.98,.82)),
                          ('0F271606',(1.14,.91,.74)),('0F3A2A1B',(.88,1.04,.92))]:
        rgb=np.asarray(block).copy()
        rgb[:,:,:3]=np.clip(rgb[:,:,:3].astype(float)*tint,0,255).astype(np.uint8)
        art=Image.fromarray(rgb)
        for j,key in enumerate(keys):
            x=j%2*32;y=j//2*32
            for fade,factor in [(0,1),(1,.60),(2,.26)]:
                c=''.join('0F' if n in (13,14,15) or n<16*fade else f'{n-16*fade:02X}'for n in bytes.fromhex(palette))
                if len(set(bytes.fromhex(c)))<2:continue
                cell=art.crop((x,y,x+32,y+32))
                p.tile(NORMAL,key,c,cell if not fade else light(cell,factor))


def cell(canvas,x,y):
    sx=ORIGIN[0]+x*4;sy=ORIGIN[1]+y*4
    return canvas.crop((sx,sy,sx+32,sy+32))


def register_family(p,scope,poses,palettes,regular,include_fragments=True):
    """One complete painted pose per live head, plus actual surviving pieces if clipped."""
    byhead=defaultdict(list)
    for pose in poses:byhead[pose['head']].append(pose)
    bypart=defaultdict(list)
    for head,variants in byhead.items():
        variants.sort(key=lambda q:-q['order'])
        for q in variants:
            for dx,dy,key,h,v in [(0,0,head,0,0),*q['parts']]:
                entry=(head,dx,dy,h,v,q)
                bypart[key].append(entry)
        for pal in palettes:
            offsets={(x,y) for k,c,x,y in p.adds if k==head and c==pal}
            for q in variants:
                left,top,right,bottom=q['canvas'].getbbox()
                for y in range((top//32)*8-24,((bottom+31)//32)*8-24,8):
                    for x in range((left//32)*8-40,((right+31)//32)*8-40,8):offsets.add((x,y))
            for x,y in sorted(offsets):
                vk,vc=p.virtual(head,pal,x,y)
                for q in variants:
                    crop=cell(q['canvas'],x,y)
                    if pal!=regular:crop=light(crop,1.27)
                    for dx,dy,marker in q['markers']:
                        p.tile(scope+'&'+p.adjacent(dx-x,dy-y,marker),vk,vc,crop)
                fallback=next(q for q in variants if q.get('default'))
                crop=cell(fallback['canvas'],x,y)
                p.tile(scope,vk,vc,crop if pal==regular else light(crop,1.27))
    for key,entries in bypart.items():
        for pal in palettes:
            if key not in byhead:
                # Some older packs attach an entire second soldier to his torso.
                # The head now owns the full figure, including the clipped pose.
                for (owner,color,_,_),(vk,vc) in p.adds.items():
                    if owner==key and color==pal:p.tile(scope,vk,vc,CLEAR)
            for head,dx,dy,h,v in sorted({entry[:5] for entry in entries}):
                near='' if key==head else '&'+p.adjacent(dx*(1 if h else -1),dy*(1 if v else -1),head)
                p.tile(scope+near,key,pal,CLEAR)
            if key in byhead or not include_fragments or pal!=regular:continue
            # Orphaned native limbs are visible when a head slips above the camera.
            # Keep the greatest amount of painted coverage among legitimate poses.
            def get(q):
                _,dx,dy,h,v,pose=q
                im=cell(pose['canvas'],dx,dy)
                if h:im=ImageOps.mirror(im)
                return ImageOps.flip(im) if v else im
            choices=[get(e) for e in entries if e[-1].get('fragment',True)]
            if choices:p.tile(scope,key,pal,max(choices,key=lambda im:np.asarray(im)[:,:,3].sum()))


def blue_squad(p,repair):
    native=json.loads((ROOT/'capture/area2/enemy-poses.json').read_text())
    signatures={r['id']:r['signature'] for r in json.loads((ROOT/'validation/v0110-enemy-poses.json').read_text())['poses']}
    norms={r['id']:recolor_cloth(Image.open(ROOT/f"validation/pose-previews/area2/{r['id']}.png").convert('RGBA'))for r in native}
    poses=[]
    for r in native:
        i=r['id']
        poses.append(dict(head=r['head'],parts=r['parts'],canvas=norms[i],order=20 if i in (3,4,5)else 10,
                          markers=[k[:3]for k in signatures[i]],default=i in (0,2,4,5,18,19)))
    head,_,_,canopy=json.loads((DATA/'chute.json').read_text())[0]
    seated=Image.new('RGBA',(384,320))
    for (a,c,x,y),(vk,vc) in p.adds.items():
        if (a,c)!=(head,BLUE):continue
        for guards,f in p.bykey[vk]:
            if f[2]==BLUE and 'area8' in guards and any(canopy in p.old_conditions.get(g,'')for g in guards):
                seated.paste(p.art(f),(160+x*4,96+y*4));break
    assert seated.getbbox() and seated.getbbox()[1]<65
    poses.append(dict(head=head,parts=[],canvas=seated,order=100,fragment=False,
                      markers=[(0,-8,canopy),(8,-8,canopy),(0,-7,canopy),(8,-7,canopy)]))
    # The other running head shares an Area 6 soldier graphic but needs this
    # squad's uniform. Replace every previous extension attached to this head.
    alt=repair['runner'];poses.append(dict(head=alt['head'],parts=alt['parts'],canvas=norms[2],
                                         order=0,markers=[],default=True))
    register_family(p,GOLD,poses,[BLUE,'FF36060F','FF202A0F',RED],BLUE)


def painted_palette(p, bodies, source, targets, scope, source_guard):
    """Retarget the whole native and virtual assembly, including conditional poses."""
    anchors=list(p.adds.items())
    for target in targets:
        patterns={k:k for k in sorted(bodies)}
        for (head,color,x,y),(vk,vc) in anchors:
            if head in bodies and color==source and any(source_guard(g) and f[2]==vc for g,f in p.bykey[vk]):
                patterns[vk]=p.virtual(head,target,x,y)[0]
        for original,new in patterns.items():
            for g,f in p.bykey[original]:
                if not source_guard(g) or f[2]!=source:continue
                cond=[scope]
                for name in g:
                    if name in NORMAL.split('&') or name in ('a8Room39','a8Core'):continue
                    rule=p.old_conditions.get(name,'')
                    if rule.startswith('spriteNearby,'):
                        _,x,y,key,_,_=rule.split(',')
                        # Bounds, mirror and local pose selectors retain the donor ordering.
                        name=p.adjacent(int(x),int(y),key)
                    cond.append(name)
                im=p.art(f)
                p.tile('&'.join(cond),new,target,light(im,1.24) if target!=source else im)


def machines(p, records,repair):
    actors=records['new_actors']
    cable={k for q in actors['cable'] for x,y,k,h,v in q['parts']}
    cable.update(q[2]for q in actors['cable_mount'])
    painted_palette(p,cable,RED,['FF30150F','FF36060F','FF202A0F'],CABLE,lambda g:'a8Room39' in g)
    painted_palette(p,set(repair['dispatcher']),RED,['FF36060F','FF202A0F',BLUE],GOLD,
                    lambda g:'area8'in g and not any(v.startswith('a8Room') for v in g))
    painted_palette(p,set(repair['rifle_hit']),RED,['FF30150F'],NORMAL+'&a8Room7',
                    lambda g:g[:3]==['!interception','!interception14','!area13'] and '!title' in g)
    for hit,normal in [('FF201515','FF36060F'),('FF202015','FF202A0F')]:
        painted_palette(p,set(repair['swing_hit'][hit]),normal,[hit],GOLD,
                        lambda g:g[:3]==['!interception','!interception14','!title']
                        or ('!interception' in g and ('weaponWide' in g or 'weaponRocket' in g)))
    # Disconnected shield pieces should reveal the same approved shield painting at an edge.
    sheet=Image.open(ART/'area4-shield-walk.png').convert('RGBA')
    art=[cropped(sheet.crop((i*sheet.width//3,0,(i+1)*sheet.width//3,sheet.height)))for i in range(3)]
    suspect={k for k,c,n,rooms in repair['fallbacks'] if rooms==[32] and c=='FF30160F'}
    for state in actors['shield']:
        anchor=state['anchor']
        idx=(1 if anchor.startswith('0402') else 2) if state['pose']=='walk' else 0
        canvas=Image.new('RGBA',(96,128));canvas.alpha_composite(art[idx].resize((90,125),LANCZOS),(3,2))
        for x,y,k,h,v in state['parts']:
            sx,sy=(x+8)*4,y*4
            for key,palette,_ in repair['other_edges']:
                if k==key and palette.startswith('FF'):
                    # The shield carrier overlaps Spencer for one frame in the reactor.
                    # With a painted head present that head already supplies this piece.
                    p.tile(CORE+'&'+p.adjacent(-x,-y,anchor),k,palette,CLEAR)
                    p.tile(CORE,k,palette,light(canvas.crop((sx,sy,sx+32,sy+32)),1.18))
            if k not in suspect:continue
            p.tile(CORE+'&'+p.adjacent(-x,-y,anchor),k,'FF30160F',CLEAR)
            if x==-8:
                crop=canvas.crop((sx,sy,sx+32,sy+32))
                p.tile(CORE,k,'FF30160F',crop)
    # A narrow rail muzzle flare flashes for several frames on each shot.
    # Reuse the middle, in the forward direction, of the approved rifle flash.
    burst='0000000000010503080405178F6E1A0C'
    options=[f for g,f in p.bykey[burst] if 'area6' in g and f[0]=='23']
    assert options
    corner=p.art(options[0]);full=Image.new('RGBA',(64,64))
    for x in (0,1):
        for y in (0,1):
            q=ImageOps.mirror(corner) if x else corner
            full.paste(ImageOps.flip(q) if y else q,(32*x,32*y))
    flare=Image.new('RGBA',(32,32))
    flare.alpha_composite(cropped(full).resize((30,16),LANCZOS),(1,8))
    p.tile(NORMAL,'0000001C00000000600CFF6304300000',BLUE,flare)
    for c in sorted({c for _,k,c in records['sprites'] if k==burst}|{'FF30150F','FF36150F','FF30210F'}):
        p.tile(NORMAL,burst,c,corner)


def chamber(p, blocks):
    scope=NORMAL+'&'+p.condition('a851SpikeChamber','ppuMemoryCheckConstant,3F0A,==,16')
    # These are the same framed industrial mesh panels as the Area 3 recording.
    # Each factory-made edge and corner matches its existing NES quadrant.
    seen=set()
    for number in (5,6,8,9,10,11):
        for key,color in blocks[str(number)]:
            if key in seen:continue
            seen.add(key)
            fields=next(f for g,f in p.bykey[key] if f[0]=='14' and f[2]=='0F11020B')
            p.tile(scope,key,color,p.art(fields))
    # Use the existing shaft's brushed metal for the overhead suspension block.
    material=Image.open(ART/'area8-materials.png').convert('RGB')
    w,h=material.size
    steel=material.crop((int(w*.68),int(h*.56),int(w*.73),int(h*.59))).resize((58,38),LANCZOS)
    plate=Image.new('RGBA',(64,64));d=ImageDraw.Draw(plate)
    d.rounded_rectangle((0,3,63,48),radius=5,fill='#27363d',outline='#82929a',width=2)
    plate.alpha_composite(steel.convert('RGBA'),(3,6))
    d.line((4,6,59,6),fill='#d1d9d6',width=2)
    for x in (18,43):
        d.rounded_rectangle((x-5,12,x+5,37),radius=3,fill='#101a20',outline='#41515a',width=2)
        d.line((x+4,15,x+4,34),fill='#aaafa6')
    for x in (5,58):
        for y in (9,40):
            d.ellipse((x-2,y-2,x+2,y+2),fill='#3a464c',outline='#9ba7a8')
    for j,(key,color) in enumerate(blocks['7']):
        x=j%2*32;y=j//2*32
        p.tile(scope,key,color,plate.crop((x,y,x+32,y+32)))


def scrolling_edges(p, modules, repairs):
    # Reuse the Area 8 material painter for CHR that appeared only on a scrolling
    # edge. These exact pattern/palette pairs were traced in the complete replay.
    records={'background':repairs['scroll_edges']}
    if not records['background']:return
    begin=len(p.tiles)
    p.backgrounds=[]
    terrain(p,records,modules)
    known={(key,color) for _,key,color in records['background']}
    result=[]
    last_resort={}
    for line in p.tiles[begin:]:
        guard,fields=split(line,'<tile>')
        if (fields[1],fields[2]) in known and not any('a8N' in s for s in guard):
            result.append(line)
            last_resort.setdefault((fields[1],fields[2]),f'[{NORMAL}]<tile>'+','.join(fields))
    assert known==set(last_resort), known-set(last_resort)
    p.tiles[begin:]=result+list(last_resort.values())


def score_text(p, glyph, palette):
    from PIL import ImageDraw,ImageFont
    if palette=='0F200F0F':
        shape=Image.new('RGBA',(32,32))
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',29)
        ImageDraw.Draw(shape).text((16,16),'8',anchor='mm',font=font,fill=(233,231,211))
        p.tile('area8&areaClear',glyph,palette,shape)
        zero='384CC6C6C66438000000000000000000'
        f=next(f for g,f in p.bykey[zero] if 'area2' in g and 'areaClear' in g and f[2]==palette)
        p.tile('area8&areaClear',zero,palette,p.art(f))
        return
    # Keep the native ink width and baseline used by the previous radio letters.
    # Scale2x preserves the block capitals and rounds the corners of the diagonals.
    ink=(bits(glyph)!=0).astype(np.uint8)*255
    for _ in range(2):
        pad=np.pad(ink,1,mode='edge')
        up,left,right,down=pad[:-2,1:-1],pad[1:-1,:-2],pad[1:-1,2:],pad[2:,1:-1]
        diagonal=(up!=down)&(left!=right)
        enlarged=np.empty((ink.shape[0]*2,ink.shape[1]*2),np.uint8)
        for y,x,a,b in [(0,0,left,up),(0,1,up,right),(1,0,left,down),(1,1,down,right)]:
            enlarged[y::2,x::2]=np.where(diagonal & (a==b),a,ink)
        ink=enlarged
    im=Image.new('RGBA',(32,32),(173,173,173,255))
    im.putalpha(Image.fromarray(ink).filter(ImageFilter.GaussianBlur(.38)))
    for room in ('a8RadioA','a8RadioB'):
        p.tile('area8&'+room,glyph,palette,im)


def fallback_repairs(p,repair):
    # These rules run only after all known complete poses have had a chance to
    # render. They cover clipped parts, transient colors and single-scanline edges.
    for k,c,n,rooms in repair['fallbacks']:
        opts=p.bykey[k]
        if c in ('0F200F0F','0F102109'):
            continue
        if not c.startswith('FF'):
            options=[f for g,f in opts if 'area8'in g and f[0]=='27']
            if not options:continue
            best=next((f for f in options if f[2]==c),options[0])
            p.tile(NORMAL,k,c,p.art(best))
            continue
        # Select the matching, already-painted component from its native palette.
        if n in (2020,3050):source=RED if n==2020 else 'FF202A0F'
        elif c=='FF201515':source='FF36060F'
        elif c=='FF202015':source='FF202A0F'
        else:source=BLUE
        choices=[f for g,f in opts if g==NORMAL.split('&') and f[2]==source and f[0] not in ('6','0')]
        if not choices:
            choices=[f for g,f in opts if 'area6'in g and f[0]=='23' and f[2]==c and len(g)<=10]
        if not choices:
            choices=[f for g,f in opts if not g and f[2]==source]
        if not choices:
            choices=[f for g,f in opts if '!title' in g and f[2]==source and not any(s.startswith('area')for s in g)]
        if not choices:
            choices=[f for g,f in opts if not g and f[2].startswith('FF')]
        if not choices:continue
        im=p.art(choices[0])
        if c!=source:im=light(im,1.16)
        p.tile(NORMAL,k,c,im)


def build(source,dest):
    p=Revision(source)
    records=json.loads((DATA/'field.json').read_text())
    modules=json.loads((DATA/'modules.json').read_text())
    repairs=json.loads((DATA/'regression.json').read_text())
    spikes(p,modules)
    blue_squad(p,repairs)
    machines(p,records,repairs)
    chamber(p,repairs['chamber'])
    for k,c,_,_ in repairs['fallbacks']:
        if c in ('0F200F0F','0F102109'):score_text(p,k,c)
    # Native masks and material changes are fallbacks, below pre-existing
    # rules as well as the complete assemblies in this revision.
    primary=len(p.tiles)
    fallback_repairs(p,repairs)
    scrolling_edges(p,modules,repairs)
    p.lines.extend(p.tiles[primary:])
    p.tiles=p.tiles[:primary]
    p.save(source,dest)


if __name__=='__main__':
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('source',type=Path)
    args.add_argument('dest',type=Path)
    ns=args.parse_args()
    build(ns.source,ns.dest)
