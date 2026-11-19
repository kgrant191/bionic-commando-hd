"""Build the Area 8 screenshot regression over the installed v0.15.1 pack."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import shutil

from PIL import Image, ImageOps, ImageEnhance
from build_v0150 import ART, DATA, ROOT, NORMAL, CLEAR, LANCZOS, cropped, split, EMPTY
from build_v0151 import Revision, register_family, CABLE, CORE, GOLD, BLUE, RED, ORIGIN, light, painted_palette

ATLAS='area8-review-v0152.png'

class Pack(Revision):
    def __init__(self,src):
        self.lines=(src/'hires.txt').read_text().splitlines()
        assert 'v0.15.1' in self.lines[0]
        self.sheets=[Image.open(src/s[5:]).convert('RGBA') for s in self.lines if s.startswith('<img>')]
        self.idx=len(self.sheets)
        self.cells,self.tiles,self.conditions,self.new_add,self.fallbacks={},[],{},[],[]
        self.bykey,self.old_conditions,self.adds=defaultdict(list),{},{}
        for line in self.lines:
            if '<tile>' in line:
                g,f=split(line,'<tile>');self.bykey[f[1]].append((g,f))
            elif line.startswith('<condition>'):
                k,v=line[11:].split(',',1);self.old_conditions[k]=v
            elif line.startswith('<addition>'):
                k,c,x,y,v,vc,_=line[10:].split(',');self.adds[k,c,int(x),int(y)]=v,vc

    def export(self,src,dst):
        dst.mkdir(parents=True,exist_ok=True)
        for f in src.iterdir():
            if f.name not in ('hires.txt','README.txt'):shutil.copyfile(f,dst/f.name)
        atlas=Image.new('RGBA',(1280,32*((len(self.cells)+39)//40)))
        for pixels,i in self.cells.items():atlas.paste(Image.frombytes('RGBA',(32,32),pixels),(i%40*32,i//40*32))
        atlas.save(dst/ATLAS,optimize=True)
        at=next(i for i,s in enumerate(self.lines)if '<tile>'in s)
        self.lines[at:at]=[f'<img>{ATLAS}',*[f'<condition>{k},{v}'for k,v in self.conditions.items()],*self.review_backgrounds,*dict.fromkeys(self.tiles),*dict.fromkeys(self.fallbacks)]
        self.lines.extend(self.new_add);self.lines[0]='# Bionic Commando HD v0.15.2 - Area 8 screenshot regression'
        (dst/'hires.txt').write_text('\n'.join(self.lines)+'\n')
        readme=(src/'README.txt').read_text().replace('v0.15.1','v0.15.2',1)
        readme=readme.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nArea 8 runner and parachute transitions, shield guards, damage poses, blast and projectile frames, doorways and steel flooring.\n\nPREVIOUS BUILDS\n',1)
        (dst/'README.txt').write_text(readme)


def quadrant(sheet,index):
    w,h=sheet.size
    x,y=index%2,index//2
    return sheet.crop((x*w//2,y*h//2,(x+1)*w//2,(y+1)*h//2))

def tile_at(image,x,y):
    return image.crop((x,y,x+32,y+32))

def environment(p,d):
    mat=Image.open(ART/'area8-facilities-v0152.png').convert('RGBA')
    for keys,c,index in [(d['door'],'0F13020B',0),(d['door'],'0F221202',0),(d['copper_door'],'0F261606',1)]:
        door=quadrant(mat,index).resize((128,128),LANCZOS)
        # Shared blank cells also cover thousands of unrelated openings. Each
        # interior tile needs a matching lintel or jamb in the physical doorway.
        for y,row in enumerate(keys):
            for x,key in enumerate(row):
                im=tile_at(door,x*32,y*32)
                if y>=2 or key==EMPTY:
                    dx=0 if x<2 else 3
                    g=p.near((dx-x)*8,-y*8,keys[0][dx],c,'tileNearby')
                    p.tile(NORMAL+'&'+g,key,c,im)
                else:
                    p.tile(NORMAL,key,c,im)
        # Repeated lower side-post cells can scroll on before the lintel.
        for x in (0,3):p.tile(NORMAL,keys[-1][x],c,tile_at(door,32*x,96))
    front=quadrant(mat,2).resize((64,64),LANCZOS)
    mesh=quadrant(mat,3).resize((64,64),LANCZOS)
    # Two orientations in the source ROM: a walkable edge and a lower facing.
    for i,im in [(13,ImageOps.flip(front)),(16,front),(67,front),(87,front)]:
        for j,(key,_) in enumerate(d['platforms'][str(i)]):
            if key==EMPTY or (i in (67,87) and j<2):continue
            p.tile(NORMAL,key,'0F201000',tile_at(im,32*(j%2),32*(j//2)))
    # This is the breakable hatch. Its top must meet both adjoining floor tiles.
    # Keep a recessed joint and grating to distinguish it from solid terrain.
    painted=Image.open(ART/'area8-materials.png').convert('RGBA')
    w,h=painted.size
    green=painted.crop((w//2,0,w,round(h*.142))).resize((64,52),LANCZOS)
    for col in ('0F201000','0F372717','0F3A2A1A','0F3A2A1B'):
        defaults=[]
        for side,prefix in [('green','0F3A2A1A'),('gold','0F372717'),('silver','0F201000')]:
            im=mesh.copy()
            top=front if side=='silver' else green
            if side=='gold':
                from build_v0150 import bronze
                top=bronze(top)
            im.paste(top.crop((0,0,64,13)),(0,0))
            if side=='silver':im=ImageEnhance.Brightness(im).enhance(1.15)
            for j,(key,_) in enumerate(d['platforms']['45']):
                x=j%2;y=j//2
                cells=d['platforms']['16' if side=='silver' else '1']
                # The two pairs in each breakable 16x16 block share an 8x8
                # pattern; match the neighboring material before the fallback.
                for delta,other in [(-1-x,1),(2-x,0)]:
                    match=p.near(8*delta,-8*y,cells[other][0],prefix,'tileNearby')
                    p.tile(NORMAL+'&'+match,key,col,tile_at(im,32*x,32*y))
            if (side=='gold' and col=='0F372717') or (side=='silver' and col=='0F201000') or (side=='green' and '3A' in col):
                for j,(key,_) in enumerate(d['platforms']['45']):
                    if j%2==0:defaults.append((key,tile_at(im,0,32*(j//2))))
        for key,cell in defaults:p.tile(NORMAL,key,col,cell)


def effects(p,d):
    sheet=Image.open(ART/'area8-blasts-v0152.png').convert('RGBA')
    for index,phase in enumerate(('5025','5030','5037')):
        size=64 if not index else 128
        im=cropped(quadrant(sheet,index)).resize((size,size),LANCZOS)
        northwest=[r for r in d['burst_layout'][phase] if not r[3] and not r[4]]
        for x,y,key,_,_ in sorted(northwest,key=lambda r:r[1]):
            for color in d['effect_colors'][key]:
                guard=NORMAL
                if index==2 and y==0:guard+='&'+p.adjacent(8,0,key)
                p.tile(guard,key,color,tile_at(im,x*4,y*4))
    # The original NES pattern points left in its unmirrored form.
    dart=Image.new('RGBA',(32,32))
    art=ImageOps.mirror(cropped(quadrant(sheet,3))).resize((32,14),LANCZOS)
    dart.alpha_composite(art,(0,9))
    for color in d['effect_colors'][d['dart']]:p.tile(NORMAL,d['dart'],color,dart)


def red_runner(p,d):
    a=d['runner']
    canvas=Image.open(ROOT/'validation/pose-previews/area2/2.png').convert('RGBA')
    pose=dict(head=a['head'],parts=a['parts'],canvas=canvas,default=True,order=0,markers=[])
    register_family(p,NORMAL,[pose],[RED,'FF30150F'],RED)


def parachute(p,d):
    head,_,_,canopy=json.loads((DATA/'chute.json').read_text())[0]
    src=cropped(Image.open(ART/'area8-chute-v0152.png').convert('RGBA'))
    w,h=src.size
    # Anchor the new helmet at the native head. Keep a game-sized canopy while
    # preserving the same man's build through descent and landing.
    cut=round(h*.51);can=src.crop((0,0,w,cut)).resize((119,83),LANCZOS)
    body=src.crop((0,cut,w,h)).resize((156,113),LANCZOS)
    pic=Image.new('RGBA',(384,320))
    pic.alpha_composite(can,(117,12));pic.alpha_composite(body,(98,94))
    ground=json.load(open(ROOT/'capture/area2/enemy-poses.json'))
    sig={r['id']:r['signature'] for r in json.load(open(ROOT/'validation/v0110-enemy-poses.json'))['poses']}
    from build_v0150 import recolor_cloth
    normal={g['id']:recolor_cloth(Image.open(ROOT/f"validation/pose-previews/area2/{g['id']}.png").convert('RGBA'))for g in ground if g['head']==head}
    likely=normal[0]
    offsets={(x,y) for k,c,x,y in p.adds if k==head and c==BLUE}
    offsets.update((x,y)for y in range(-24,32,8)for x in range(-16,32,8))
    floor=[(k,c)for j in ('1','16','59')for k,c in d['platforms'][j]]
    floor.extend([(k,'0F372717')for k,_ in d['platforms']['1']])
    floor=list(dict.fromkeys(floor))
    for x,y in sorted(offsets):
        vk,vc=p.virtual(head,BLUE,x,y)
        def cutcell(im):return tile_at(im,ORIGIN[0]+4*x,ORIGIN[1]+4*y)
        seated=cutcell(pic)
        for dx,dy,marker in [(0,-8,canopy),(8,-8,canopy),(0,-7,canopy),(8,-7,canopy)]:
            p.tile(GOLD+'&'+p.adjacent(dx-x,dy-y,marker),vk,vc,seated)
        # On an airborne frame Mesen may receive the head without any canopy
        # tiles. A true landing puts the feet on the stage's structural surface.
        for k,c in floor:
            for xx,fy in ((1,30),(9,30),(1,33),(9,33)):
                g=p.near(xx-x,fy-y,k,c,'tileNearby')
                for ident,canvas in normal.items():
                    for dx,dy,marker,*_ in sig[ident]:
                        p.tile(GOLD+'&'+g+'&'+p.adjacent(dx-x,dy-y,marker),vk,vc,cutcell(canvas))
                p.tile(GOLD+'&'+g,vk,vc,cutcell(likely))
        p.tile(GOLD,vk,vc,seated)

def shields(p):
    records=json.loads((DATA/'field.json').read_text())['new_actors']['shield']
    sheet=Image.open(ART/'area4-shield-walk.png').convert('RGBA')
    poses=[]
    for j in range(3):
        art=cropped(sheet.crop((j*sheet.width//3,0,(j+1)*sheet.width//3,sheet.height)))
        art=art.resize((round(art.width*125/art.height),125),LANCZOS)
        crown=art.crop((0,0,art.width,22)).getchannel('A').point(lambda a:255 if a>95 else 0).getbbox()
        canvas=Image.new('RGBA',(384,320))
        canvas.alpha_composite(art,(ORIGIN[0]+15-(crown[0]+crown[2])//2,ORIGIN[1]+2))
        poses.append(canvas)
    for head in sorted({r['anchor'] for r in records}):
        states=[r for r in records if r['anchor']==head]
        walking=1 if head.startswith('0402') else 2
        primary=walking if max(states,key=lambda r:r['count'])['pose']=='walk' else 0
        parts={tuple(q)for r in states for q in r['parts']}
        # These two physical anchors are unique to the shield carrier. Either
        # can carry the painted pose when the object's other half is culled.
        spare=next(k for x,y,k,h,v in parts if x==0 and y==8 and k.startswith(('736121','61213F')))
        for col in ['FF30160F','FF202A0F']:
            for anchor,offset in ((head,0),(spare,8)):
                offsets={(x,y)for k,c,x,y in p.adds if k==anchor and c==col}
                offsets.update((x,y-offset)for x in range(-16,32,8)for y in range(0,32,8))
                for x,y in sorted(offsets):
                    vk,vc=p.virtual(anchor,col,x,y)
                    if offset:
                        p.tile(CORE+'&'+p.adjacent(-x,-offset-y,head),vk,vc,CLEAR)
                    for pix,markers in [(walking,['01010B','318870']), (0,['128A71','3211E0'])]:
                        for dx,dy,key,h,v in parts:
                            if dx==0 and dy==24 and any(key.startswith(a)for a in markers):
                                p.tile(CORE+'&'+p.adjacent(-x,dy-y-offset,key),vk,vc,tile_at(poses[pix],160+4*x,96+4*(y+offset)))
                    p.tile(CORE,vk,vc,tile_at(poses[primary],160+4*x,96+4*(y+offset)))
                p.tile(CORE,anchor,col,CLEAR)
            for dx,dy,key,h,v in parts:
                if key in (head,spare,EMPTY):continue
                for anchor,ay in ((head,0),(spare,8)):
                    p.tile(CORE+'&'+p.adjacent(-dx,ay-dy,anchor),key,col,CLEAR)

def hero(p,d):
    # Match the original equipped-weapon renderer for every observed hurt
    # pattern, including the reactor-only stretched swing and recoil.
    for target,source in [('FF202015','FF202A0F'),('FF201515','FF36060F')]:
        def donor(g):
            if any(a.startswith(('a8','area'))for a in g):return False
            return '!title' in g and ('weaponWide'in g or 'weaponRocket'in g or '!interception'in g)
        painted_palette(p,set(d['hurt'][target]),source,[target],NORMAL,donor)
        for key in d['hurt'][target]:
            # Some base tiles are painted fragments instead of metasprite cells.
            choices=[f for g,f in p.bykey[key] if not g and f[2]==source]
            if choices:p.tile(NORMAL,key,target,light(p.art(choices[0]),1.16))

def stable_shoulders(p,dst):
    # Recoil can put the standing head and torso at either end of the OAM
    # work page, or at both ends several pixels apart. Both banks compete for
    # one foreground layer, so the renderer paints exactly one equipped actor.
    head='000102F17A797A7E52FFFE8F7E67064E'
    torso='FFFF0FFF0F0701000606FFF109070100'
    scopes=[]
    for tag,head_addr,body_addr,y_addr,facing_addr,x_addr in (
            ('A','021D','0221','021C','021E','021F'),
            ('B','02E5','02E1','02E4','02E6','02E7')):
        guards=[CORE]
        for label,adr,value in [('Head',head_addr,'86'),('Body',body_addr,'87')]:
            guards.append(p.condition('a852'+label+tag,f'memoryCheckConstant,{adr},==,{value}'))
        guards.append(p.condition('a852Live'+tag,f'memoryCheckConstant,{y_addr},<,EF'))
        facing=p.condition('a852Facing'+tag,f'memoryCheckConstant,{facing_addr},==,40,40')
        scopes.append(('&'.join(guards),facing,x_addr,y_addr,tag))
    keys={head,torso}
    # Include the eight standing body cells already rendered by the same painting.
    keys.update(json.loads((DATA/'review-v0152.json').read_text())['standing'])
    additions=list(p.adds.items())
    swing='3E7EFC5A24382040325A8CE6FCF8E0C0'
    def local_pose(key,x,y):
        if key!=head:return ''
        marker=p.adjacent(7-x,-y,swing).split('&')[-1]
        return '&!'+marker
    for scope,*_ in scopes:
        for color in ('FF36060F','FF201515','FF202A0F','FF202015'):
            for k in keys:
                for weapon in ('weaponRocket','weaponWide'):
                    p.tile(scope+'&'+weapon+local_pose(k,0,0),k,color,CLEAR)
            for (k,c,x,y),(v,vc)in additions:
                if k in keys and c==color:
                    for weapon in ('weaponRocket','weaponWide'):p.tile(scope+'&'+weapon+local_pose(k,x,y),v,vc,CLEAR)
    bg=[]
    for weapon,name in [('weaponRocket','spencer-rocket-v0100.png'),('weaponWide','spencer-wide-v0100.png')]:
        sheet=Image.open(ART/name).convert('RGBA');w,h=sheet.size
        part=cropped(sheet.crop((0,0,w//4,h//4)))
        sprite=part.resize((round(part.width*122/part.height),122),LANCZOS)
        for mir in (False,True):
            art=ImageOps.mirror(sprite) if mir else sprite
            crown=art.crop((0,0,art.width,12)).getchannel('A').point(lambda a:255 if a>100 else 0).getbbox()
            # Leave space beyond the NES viewport for the sprite. Scroll
            # offsets stay positive over the entire visible range of OAM.
            plate=Image.new('RGBA',(1152,1104))
            plate.alpha_composite(art,(1024+16-(crown[0]+crown[2])//2,960))
            filename='area8-recoil-'+weapon+('-right' if mir else '-left')+'-v0152.png'
            dst.mkdir(exist_ok=True,parents=True);plate.save(dst/filename,optimize=True)
            for scope,facing,x_addr,y_addr,tag in scopes:
                guard=scope+'&'+weapon+'&'+('' if mir else '!')+facing
                for x in range(0,256,4):
                    cx=p.condition('a852SX'+tag+str(x),f'memoryCheckConstant,{x_addr},==,{x:02X},FC')
                    for y in range(0,240,4):
                        cy=p.condition('a852SY'+tag+str(y),f'memoryCheckConstant,{y_addr},==,{y:02X},FC')
                        # CPU work RAM can prepare the next pose one frame before
                        # the PPU changes it. Keep the still-visible swinging arm.
                        marker_x=x+(-7 if mir else 7)
                        neg=[]
                        for xx in range((marker_x-8)//8*8,(marker_x+15)//8*8+1,8):
                            for yy in range((y-5)//8*8,(y+17)//8*8+1,8):
                                if not (0<=xx<256 and 0<=yy<240):continue
                                name=p.condition(f'a852Swing{xx}_{yy}',f'spriteAtPosition,{xx},{yy},{swing},FF202A0F,Y')
                                neg.append('!'+name)
                        screen='&'.join(neg)
                        bg.append(f'[{guard}&{cx}&{cy}&{screen}]<background>{filename},1,0,0,29,{256-x-1},{240-y-2}')
    return bg

def build(src,dst):
    p=Pack(src)
    d=json.loads((DATA/'review-v0152.json').read_text())
    environment(p,d);effects(p,d);red_runner(p,d);parachute(p,d);shields(p)
    first=len(p.tiles)
    hero(p,d)
    last=len(p.tiles);foreground=stable_shoulders(p,dst)
    p.tiles=p.tiles[:first]+p.tiles[last:]+p.tiles[first:last]
    # Use the existing stage machinery in the recessed openings of the final
    # room. The gameplay palette controls the same fade as the normal level.
    bg=[]
    for i,brightness in [(0x33,.40),(0x23,.24),(0x13,.11)]:
        guard=p.condition('a852CoreLight'+str(i),f'ppuMemoryCheckConstant,3F01,==,{i:02X}')
        bg.append(f'[{CORE}&screenEnabled&{guard}]<background>area8-machinery-wall-v0150.png,{brightness},0,0,2')
    for pal in ('0F221202','0F332313','0F372716','0F201000'):
        p.tile(CORE,EMPTY,pal,CLEAR)
    p.review_backgrounds=foreground+bg
    p.export(src,dst)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('dest',type=Path)
    args=parser.parse_args();build(args.source,args.dest)
