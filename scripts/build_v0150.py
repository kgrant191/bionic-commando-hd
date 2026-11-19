"""Build the Area 8 pack from the approved v0.14.1 assets and recorded room layouts."""
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import argparse, hashlib, json, re, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'
DATA = ROOT / 'capture/area8'
ATLAS = 'area8-machinery-v0150.png'
WALL = 'area8-machinery-wall-v0150.png'
NORMAL = 'area8&!worldmap&!equipment&!title&!radio&!areaClear'
FIELD = NORMAL + '&!a8Core&!a8RadioA&!a8RadioB&!a8Menu'
EMPTY = '0' * 32
CLEAR = Image.new('RGBA', (32,32))
LANCZOS = Image.Resampling.LANCZOS

def split(line,tag):
    guard,raw=line.split(tag)
    return guard.strip('[]').split('&') if guard else [],raw.split(',')

class Pack:
    def __init__(self,source):
        self.lines=(source/'hires.txt').read_text().splitlines()
        assert 'v0.14.1' in self.lines[0]
        self.sheets=[Image.open(source/s[5:]).convert('RGBA') for s in self.lines if s.startswith('<img>')]
        self.idx=len(self.sheets)
        self.cells={}; self.tiles=[]; self.fallbacks=[]; self.conditions={}; self.backgrounds=[]; self.new_add=[]
        self.bykey=defaultdict(list); self.old_conditions={};self.adds={}
        for s in self.lines:
            if '<tile>' in s:
                g,f=split(s,'<tile>'); self.bykey[f[1]].append((g,f))
            if s.startswith('<condition>'):
                n,rest=s[11:].split(',',1); self.old_conditions[n]=rest.split(',')
            if s.startswith('<addition>'):
                k,c,x,y,v,vc,flag=s[10:].split(',')
                self.adds[k,c,int(x),int(y)]=(v,vc)
    def condition(self,name,rule):
        assert name not in self.conditions or self.conditions[name]==rule
        self.conditions[name]=rule;return name
    def near(self,x,y,k,c,kind='spriteNearby'):
        rule=f'{kind},{x},{y},{k},{c},N'
        name=self.condition('a8N'+hashlib.md5(rule.encode()).hexdigest()[:12],rule)
        # Native PPU coordinates span [0,240). Check before pre- and post-flip lookup.
        if y<0:
            return self.condition(f'a8Yge{-y}',f'positionCheckY,>=,{-y}')+'&'+name
        if y>0:
            return self.condition(f'a8Ylt{240-y}',f'positionCheckY,<,{240-y}')+'&'+name
        return name
    def graphics(self,im):
        im=im.convert('RGBA')
        if not im.getchannel('A').getbbox():return (6,96,0)
        token=im.tobytes()
        if token not in self.cells:self.cells[token]=len(self.cells)
        i=self.cells[token];return self.idx,i%40*32,i//40*32
    def tile(self,guard,k,c,art):
        idx,x,y=art if isinstance(art,tuple) else self.graphics(art)
        self.tiles.append((f'[{guard}]' if guard else '')+f'<tile>{idx},{k},{c},{x},{y},1,N')
    def virtual(self,k,c,x,y):
        a=k,c,x,y
        if a not in self.adds:
            vk=hashlib.md5(f'area8:{k}:{x}:{y}'.encode()).hexdigest().upper()
            self.adds[a]=(vk,c); self.new_add.append(f'<addition>{k},{c},{x},{y},{vk},{c},N')
            self.fallbacks.append(f'<tile>6,{vk},{c},96,0,1,N')
        return self.adds[a]
    def art(self,f):
        i,x,y=map(int,(f[0],f[3],f[4]));return self.sheets[i].crop((x,y,x+32,y+32))
    def finish(self,source,dest):
        sheet=Image.new('RGBA',(1280,32*((len(self.cells)+39)//40)))
        for pixels,i in self.cells.items():sheet.paste(Image.frombytes('RGBA',(32,32),pixels),(i%40*32,i//40*32))
        sheet.save(dest/ATLAS,optimize=True)
        lines=self.lines.copy()
        at=next(i for i,line in enumerate(lines) if '<tile>' in line)
        lines[at:at]=[f'<img>{ATLAS}']+[f'<condition>{k},{v}'for k,v in self.conditions.items()]+self.backgrounds+list(dict.fromkeys(self.tiles))+list(dict.fromkeys(self.fallbacks))
        lines.extend(self.new_add)
        lines[0]='# Bionic Commando HD v0.15.0 - Area 8'
        (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
        doc=(source/'README.txt').read_text().replace('v0.14.1','v0.15.0',1).replace('Area 14 review build','Area 8 review build',1)
        doc=doc.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nArea 8 tower, elevators, cable enemies and reactor guards.\n\nPREVIOUS BUILDS\n',1)
        (dest/'README.txt').write_text(doc)

def bits(k):
    a=np.unpackbits(np.frombuffer(bytes.fromhex(k),np.uint8)).reshape(16,8)
    return a[:8]+2*a[8:]

def tone(im,v):
    a=im.getchannel('A');im=ImageEnhance.Brightness(im.convert('RGB')).enhance(v).convert('RGBA');im.putalpha(a);return im

def bronze(im):
    a=np.array(im);rgb=a[:,:,:3].astype(float);g=rgb[:,:,1];m=(g>rgb[:,:,0]*1.13)&(g>rgb[:,:,2]*1.03)
    rgb[m]=np.stack([g[m]*1.22+12,g[m]*.86+7,g[m]*.34+4],1)
    a[:,:,:3]=np.clip(rgb,0,255);return Image.fromarray(a)

def terrain(pack,records,modules):
    modules={s:{int(i):v for i,v in tab.items()}for s,tab in modules.items()}
    sw=Image.open(ART/'area8-materials.png').convert('RGBA');w,h=sw.size
    def sample(coords,size):
        return sw.crop(tuple(round(v*(w if j%2==0 else h)) for j,v in enumerate(coords))).resize(size,LANCZOS)
    stone=sample((0,.001,.499,.252),(64,64))
    lower=stone.crop((0,32,64,64));stone.paste(lower.crop((16,0,64,32)),(0,32));stone.paste(lower.crop((0,0,16,32)),(48,32))
    ledge=sample((.501,.001,.999,.142),(64,52))
    lip=Image.new('RGBA',(64,64));lip.alpha_composite(ledge)
    cladding=sample((.002,.503,.165,.765),(64,64))
    pylon=sample((.503,.503,.998,.635),(128,64))
    maps={}
    def register(block,img):
        for j,(k,_) in enumerate(block):
            if k==EMPTY:continue
            x=j%2*32;y=j//2*32;maps.setdefault(k,img.crop((x,y,x+32,y+32)))
    register(modules['tower'][0],stone)
    register(modules['tower'][1],lip)
    register(modules['lift'][0],cladding)
    for j,i in enumerate([4,5]):register(modules['lift'][i],pylon.crop((j*64,0,(j+1)*64,64)))
    # Original game uses the same metal drum, floor spikes and direction signs as prior levels.
    for data,ns,pid,pc in [('tower',[47],22,'0F34230C'),('tower',[38,56],14,'0F271505'),('tower',[48,49],10,'0F201017'),('hazard',[14,15],10,'0F201017')]:
        for num in ns:
            for k,_ in modules[data][num]:
                cand=next((f for g,f in pack.bykey[k]if int(f[0])==pid and f[2]==pc),None)
                if cand and k!=EMPTY:maps[k]=pack.art(cand)
    ledge_keys={k for k,_ in modules['tower'][1]}
    # The gold side uses the same ledge profile.
    palettes={'0F13020B':[(99,124,151),(45,68,90),(24,47,59)],'0F221202':[(96,132,164),(49,76,111),(25,45,70)],
              '0F3A2A1B':[(105,140,120),(51,79,70),(32,52,49)],'0F3A2A1A':[(152,197,151),(49,120,81),(27,61,49)],
              '0F271404':[(233,159,69),(142,92,58),(76,58,65)],'0F162212':[(174,76,59),(75,104,139),(40,58,79)],
              '0F201000':[(192,204,208),(124,143,151),(70,83,91)],'0F312111':[(158,187,210),(88,129,165),(47,76,103)],
              '0F372717':[(226,179,87),(142,105,60),(83,65,47)],'0F271606':[(193,121,78),(116,65,52),(67,46,44)],
              '0F261606':[(187,111,80),(114,66,54),(65,45,46)]}
    micro=np.asarray(sample((.52,.57,.70,.72),(32,32)).convert('L')).astype(float);micro-=micro.mean()
    def machined(k,c):
        ix=bits(k)
        if k==EMPTY:return CLEAR
        # Metal contours follow the original CHR exactly. Filtering at boundaries uses a periodic
        # sample, so a vertical or horizontal pipe continues through the next cell without an end cap.
        colors=np.array([[15,23,30],*palettes[c]],float)
        scaled=np.repeat(np.repeat(ix,4,0),4,1); weights=np.stack([gaussian_filter((scaled==i).astype(float),1.13,mode='nearest') for i in range(4)],2)
        rgb=weights@colors
        val=rgb.mean(2);rgb+=(np.clip(np.roll(val,1,axis=0)-np.roll(val,-1,axis=0),-36,36)*-.31+micro*.16)[:,:,None]
        a=np.uint8(np.clip((1-weights[:,:,0])*285,0,255))
        return Image.fromarray(np.dstack((np.uint8(np.clip(rgb,0,255)),a)))
    normal_by_room={7:['0F13020B','0F3A2A1A','0F271404','0F201000'],80:['0F221202','0F372717','0F162212','0F201000'],81:['0F13020B','0F3A2A1B','0F271606','0F201000']}
    for room in (38,39,77,78,79):normal_by_room[room]=normal_by_room[7]
    for room in (82,83):normal_by_room[room]=['0F312111','0F261606','0F221202']
    # The plaque is placed only where the native four-quadrant emblem exists; its blank corner
    # cells are shared with wall openings. Match each such cell to its nonblank neighboring tile.
    emblem=Image.new('RGBA',(128,128),(55,63,70,255));d=ImageDraw.Draw(emblem)
    d.rounded_rectangle((1,1,126,126),radius=5,outline=(161,165,156),width=3)
    eagle=pack.sheets[13].getbbox();em=pack.sheets[13].crop(eagle).resize((113,58),LANCZOS)
    emblem.alpha_composite(em,(7,32))
    for x in (9,118):
        for y in (9,118):d.ellipse((x-2,y-2,x+2,y+2),fill=(174,171,150))
    grid={}
    for i,num in enumerate([50,51,54,55]):
        for j,(k,c) in enumerate(modules['tower'][num]):grid[(i%2*2+j%2,i//2*2+j//2)]=k
    for (x,y),k in grid.items():
        # Nearest unique marker is a visible part of the original eagle itself.
        ax,ay=min((pt for pt in grid if grid[pt]!=EMPTY and pt!=(x,y)),key=lambda pt:abs(pt[0]-x)+abs(pt[1]-y))
        pack.tile(FIELD+'&'+pack.near((ax-x)*8,(ay-y)*8,grid[ax,ay],'0F201000','tileNearby'),k,'0F201000',emblem.crop((32*x,32*y,32*x+32,32*y+32)))
    @lru_cache(None)
    def paint(k,c):
        if k in maps:
            return bronze(maps[k]) if c=='0F372717' and k in ledge_keys else maps[k]
        return machined(k,c)
    # Normal and faded colors use the same source art on the corresponding room palette.
    for room,k,c in records['background']:
        normal=normal_by_room[room]
        if c in normal: base,brightness=c,1
        else:
            def faded(p,n):
                return ''.join('0F' if v in (13,14,15) or v-16*n<0 else f'{v-16*n:02X}'for v in bytes.fromhex(p))
            candidates=[(p,(.58,.25)[n-1])for p in normal for n in [1,2]if faded(p,n)==c]
            if not candidates:continue
            base,brightness=candidates[0]
        im=paint(k,base)
        pack.tile(NORMAL+f'&a8Room{room}',k,c,im if brightness==1 else tone(im,brightness))
    for room,k,c in records['background']:
        pals=normal_by_room[room]
        if c not in pals:continue
        a=pack.condition('a8BgA'+pals[0][2:4],'ppuMemoryCheckConstant,3F01,==,'+pals[0][2:4])
        b=pack.condition('a8BgB'+pals[1][2:4],'ppuMemoryCheckConstant,3F05,==,'+pals[1][2:4])
        pack.tile(NORMAL+'&'+a+'&'+b,k,c,paint(k,c))
    for pals in normal_by_room.values():
        bg=f'[{NORMAL}&screenEnabled&a8BgA{pals[0][2:4]}&a8BgB{pals[1][2:4]}]<background>{WALL},1,0,0,2'
        if bg not in pack.backgrounds:pack.backgrounds.append(bg)
    for room,pals in normal_by_room.items():
        c=int(pals[0][2:4],16)
        for n,b in [(0,1),(1,.5),(2,.19)]:
            val=max(c-16*n,0) if c-16*n>=0 else 15
            flag=pack.condition('a8Light'+str(val),f'ppuMemoryCheckConstant,3F01,==,{val:02X}')
            pack.backgrounds.append(f'[{NORMAL}&a8Room{room}&screenEnabled&{flag}]<background>{WALL},{b},0,0,2')
        pack.backgrounds.append(f'[{NORMAL}&a8Room{room}&screenEnabled]<background>{WALL},0,0,0,2')

def recolor_cloth(im):
    a=np.array(im);hsv=np.asarray(im.convert('RGB').convert('HSV'))
    r,g,b=[a[:,:,j].astype(float) for j in range(3)]
    mask=((hsv[:,:,0]<=8)|(hsv[:,:,0]>=226))&(hsv[:,:,1]>40)&(r>30)
    # Cool only the burgundy fabric and enamel. The orange skin, russet leather,
    # neutral gun metal and transparent pixels retain their original color.
    value=r*.70+g*.2+b*.1
    a[:,:,0][mask]=np.clip(value[mask]*.50+4,0,255);a[:,:,1][mask]=np.clip(value[mask]*.82+7,0,255);a[:,:,2][mask]=np.clip(value[mask]*1.10+15,0,255)
    return Image.fromarray(a)

@lru_cache(None)
def approved_blue_cells():
    lookup={}
    for pose in (0,1,2,3,4,5,18,19):
        src=Image.open(ROOT/f'validation/pose-previews/area2/{pose}.png').convert('RGBA')
        blue=recolor_cloth(src)
        # Undo the old palette variation by matching its exact published tile
        # against the ungraded painting, including its alpha and crop.
        graded=np.array(src);graded[:,:,:3]=np.uint8(np.clip(graded[:,:,:3]*np.array([1.15,.72,.65]),0,255))
        old=Image.fromarray(graded)
        for y in range(0,src.height,32):
            for x in range(0,src.width,32):
                box=(x,y,x+32,y+32);cell=blue.crop(box)
                lookup[old.crop(box).tobytes()]=cell
                lookup[src.crop(box).tobytes()]=cell
    return lookup

def blue_uniform(im):
    match=approved_blue_cells().get(im.tobytes())
    return match if match is not None else im

def transplant(pack,records):
    actual=defaultdict(set)
    for room,k,c in records['sprites']:
        if room in (7,80):actual[room,c].add(k)
    def copy_actor(room,stage,ids,source,target,guard,paint_blue=False,only=None):
        keys=actual[room,target].copy()
        if only:keys&=only
        old_add=list(pack.adds.items()); virtual={}
        donor_keys={f[1] for k in keys for g,f in pack.bykey.get(k,[]) if stage in g and int(f[0]) in ids and f[2]==source}
        for (anchor,c,dx,dy),(vk,vc) in old_add:
            if c!=source or anchor not in keys:continue
            if not any(stage in g and int(f[0])in ids and f[2]==vc for g,f in pack.bykey.get(vk,[])):continue
            virtual[vk]=pack.virtual(anchor,target,dx,dy)[0]
        def guards(names):
            out=[]
            for name in names:
                key=name.lstrip('!')
                if key==stage or name in NORMAL.split('&') or name in ('!interception','!interception14'):continue
                terms=pack.old_conditions.get(key,[])
                if terms and terms[0]=='spriteNearby' and source!=target and terms[-2]==source:
                    terms=terms.copy();terms[-2]=target
                    key=pack.condition('a8'+key+target[2:6],','.join(terms))
                    out.append(('!' if name.startswith('!')else'')+key)
                else:out.append(name)
            return '&'.join([guard,*out])
        for k in sorted(donor_keys|set(virtual)):
            for g,f in pack.bykey[k]:
                if stage not in g or f[2]!=source or int(f[0])not in ids:continue
                if any('Boss' in s or 'Harbor' in s for s in g):continue
                art=blue_uniform(pack.art(f)) if paint_blue else tuple(map(int,[f[0],f[3],f[4]]))
                pack.tile(guards(g),virtual.get(k,k),target,art)
    # Preserve the approved Area 6 canopy/thrower and the Area 2 grenadier's actual pose tests.
    # Limit the blue grenadier's body to the second tower. Its canopy has its own palette rules.
    copy_actor(80,'area2',{10,11},'FF30160F','FF30210F',NORMAL,True)
    copy_actor(80,'area6',{23,22,24},'FF30210F','FF30210F',NORMAL)
    copy_actor(80,'area6',{23,22,24},'FF36160F','FF36150F',NORMAL)
    for k in ['0000020E16183800000121110907077F']:
        for c in sorted({p for _,key,p in records['sprites'] if key==k}|{'FF30160F'}):
            # The round burst has a common cell mirrored around all four corners.
            k='0000020E16183800000121110907077F'
            f=next((f for g,f in pack.bykey[k]if 'area6'in g and f[0]=='22'),None)
            if f:pack.tile(NORMAL,k,c,tuple(map(int,[f[0],f[3],f[4]])))
    # The mine cycles its palette as it flies. Keep both mirrored rotor phases
    # and the impact flash tied to the matching artwork through that cycle.
    mine_keys={k for _,k,c in records['sprites'] if k.startswith(('03FFFBA3','030707A3','FFF31128'))}
    for k in sorted(mine_keys):
        for c in sorted({p for _,key,p in records['sprites'] if key==k}):
            src=c if c in {'FF30210F','FF202A0F','FF36060F'} else 'FF36160F'
            choices=[(g,f) for g,f in pack.bykey[k] if 'area6' in g and f[0]=='24']
            for mirror in ['hmirror','!hmirror']:
                ordered=sorted(choices,key=lambda item:item[1][2]!=src)
                candidate=next((f for g,f in ordered if mirror in g),None)
                if candidate:pack.tile(NORMAL+'&'+mirror,k,c,tuple(map(int,[candidate[0],candidate[3],candidate[4]])))
    for k,c,stage,idx,source in [
        ('0000183C3C180000185A24C3C3245A18','FF30160F','area5',0,'FF30150F'),
        ('0080E0F8BE2F0B0200004090E4390E03','FF201515','area6',23,'FF201515')]:
        f=next((f for g,f in pack.bykey[k] if stage in g and f[0]==str(idx)and f[2]==source),None)
        if f:pack.tile(NORMAL,k,c,tuple(map(int,[f[0],f[3],f[4]])))
    # Exact base sprites for the hydraulic elevator and the moving hazard-striped platform.
    for i,rows in enumerate(records['new_actors']['lift']):
        for dx,dy,k,c,h,v in rows:
            ind=0 if i else 14
            opts=[(g,f) for g,f in pack.bykey[k] if int(f[0])==ind and f[2].startswith('FF')]
            chosen=next(((g,f)for g,f in opts if len('&'.join(g))<100),opts[0] if opts else None)
            if chosen:
                f=chosen[1];pack.tile(NORMAL,k,c,tuple(map(int,[f[0],f[3],f[4]])))

def cropped(im):
    box=im.getchannel('A').point(lambda a:255 if a>55 else 0).getbbox()
    return im.crop(box)

def parachutist(pack):
    # The same soldier changes from his running stride to a seated harness pose
    # while the two canopy tiles sit directly above his head.
    data=json.loads((DATA/'chute.json').read_text())
    head,_,_,canopy=data[0]
    source=Image.open(ART/'area8-approved-paratrooper.png').convert('RGBA')
    source=cropped(source)
    a=np.array(source);rgb=a[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1)
    yy,xx=np.indices(r.shape)
    mask=(yy>source.height*.56)&(r>g*1.18)&(r>b*1.28)&(g<b*2.5+13)
    # The light skin on the hands and face stays warm. The helmet, sleeves and
    # trousers match the blue palette of the on-foot grenadier.
    mask&=~((r>105)&(g>r*.57)&(b<g*.76))
    val=.68*r+.23*g+.09*b
    a[:,:,0][mask]=np.clip(val[mask]*.56,0,255);a[:,:,1][mask]=np.clip(val[mask]*1.02+4,0,255);a[:,:,2][mask]=np.clip(val[mask]*1.45+10,0,255)
    painted=Image.fromarray(a)
    # Keep the crouched figure at adult scale below a compact canopy. Pin the two
    # risers to the soldier's hands after separately fitting the canopy and body.
    cut=round(painted.height*.56)
    cap=painted.crop((0,0,painted.width,cut)).resize((110,71),LANCZOS)
    body=cropped(painted.crop((0,cut,painted.width,painted.height))).resize((65,107),LANCZOS)
    canvas=Image.new('RGBA',(160,224));canvas.alpha_composite(cap,(41,31));canvas.alpha_composite(body,(64,104))
    seam=ImageDraw.Draw(canvas);seam.line((86,98,74,116), fill=(124,94,56),width=2);seam.line((108,98,119,115),fill=(142,110,64),width=2)
    stage=NORMAL;c='FF30210F'
    # Include transparent cells from the grounded overlay so its boots cannot
    # show underneath the descending pose.
    scope={(x,y)for k,p,x,y in pack.adds if k==head and p==c}
    scope.update((x,y)for x in range(-16,32,8)for y in range(-24,40,8))
    for x,y in sorted(scope):
        vk,vc=pack.virtual(head,c,x,y)
        sx=(x+16)*4;sy=(y+24)*4;cell=canvas.crop((sx,sy,sx+32,sy+32))
        for dx in [0,8]:
            pack.tile(stage+'&'+pack.near(dx-x,-8-y,canopy,c),vk,vc,cell)

def new_actors(pack,r):
    im=Image.open(ART/'area8-cable-machinery.png').convert('RGBA')
    w,h=im.size
    def asset(box):
        cut=im.crop(tuple(round(v*(w if j%2==0 else h))for j,v in enumerate(box)))
        # Remove nearly transparent matte bleed before cutting individual sprite cells.
        cut.putalpha(cut.getchannel('A').point(lambda a:0 if a<26 else min(255,round(a*1.025))))
        return cropped(cut)
    fire=asset((0,0,.49,.61));hang=asset((.50,0,1,.65))
    gun=asset((0,.66,.49,1));mount=asset((.52,.66,1,1))
    sh=Image.open(ART/'area4-shield-walk.png').convert('RGBA');sw,shh=sh.size
    shields=[cropped(sh.crop((i*sw//3,0,(i+1)*sw//3,shh)))for i in range(3)]
    for name,c,room in [('cable','FF36150F',39),('shield','FF30160F',32)]:
        group=defaultdict(list)
        for rec in r[name]:group[rec['anchor']].append(rec)
        stage=NORMAL+'&'+('a8Core' if room==32 else f'a8Room{room}')
        for anchor,poses in group.items():
            destx=-16 if name=='cable' else -8
            for yy in range(0,32,8):
                for xx in range(destx,destx+24,8):
                    vk,vc=pack.virtual(anchor,c,xx,yy)
                    for rec in sorted(poses,key=lambda a:a['count']):
                        pose=rec['pose']
                        if name=='cable':
                            src=hang if pose=='hang' else fire
                            markers=[(x,y,k)for x,y,k,_,_ in rec['parts']if x==0 and y==8 and k.startswith('E2C9' if pose=='hang'else'C9DD')]
                        else:
                            src=shields[(1 if anchor.startswith('0402')else 2) if pose=='walk' else 0]
                            markers=[(x,y,k)for x,y,k,_,_ in rec['parts']if x==0 and y==24 and k.startswith(('3188','01010B')if pose=='walk'else('128A','3211'))]
                        # Preserve the feet and the reel registration point throughout the animation.
                        sprite=src.resize((90,125),LANCZOS);canvas=Image.new('RGBA',(96,128))
                        canvas.alpha_composite(sprite,(3,2))
                        if name=='cable':
                            # A short tether joins the native moving cable to the shoulder reel.
                            d=ImageDraw.Draw(canvas);d.line((80,0,77,22),fill=(49,41,36),width=5);d.line((80,0,77,21),fill=(157,146,117),width=2)
                        sx=(xx-destx)*4;sy=yy*4
                        cell=canvas.crop((sx,sy,sx+32,sy+32))
                        for x,y,k in markers:pack.tile(stage+'&'+pack.near(x-xx,y-yy,k,c),vk,vc,cell)
                        if rec==max(poses,key=lambda a:a['count']):pack.tile(stage,vk,vc,cell)
            for dx,dy,k,flip,v in set(tuple(a) for rec in poses for a in rec['parts']):
                if k==EMPTY:continue
                gate=stage if k==anchor or name=='cable' else stage+'&'+pack.near(-dx*(-1 if flip else 1),-dy*(-1 if v else 1),anchor,c)
                pack.tile(gate,k,c,CLEAR)
    dart=Image.new('RGBA',(32,32));d=ImageDraw.Draw(dart)
    d.ellipse((3,8,26,23),fill=(38,48,54),outline=(114,131,137),width=2)
    d.polygon([(3,15),(11,9),(13,10),(13,21),(9,20)],fill=(192,205,208))
    d.rectangle((14,10,23,21),fill=(119,139,144));d.rectangle((16,11,22,13),fill=(201,207,193))
    d.rectangle((23,10,26,21),fill=(168,116,53));d.line((26,15,31,15),fill=(240,174,70),width=2)
    for room in (38,77,78,79):
        pack.tile(NORMAL+f'&a8Room{room}','087FFFEFFFFF6F18181A021A1A827F18','FF30210F',dart)
    # The native rail and hoist anchors remain independent of their moving riders.
    rail=r['rail'];pal='FF30210F';prefix=NORMAL
    center=next(q for q in rail if q[2].startswith('FFF7FF'));cx,cy,k,_,h,v=center
    canon=Image.new('RGBA',(160,96));canon.alpha_composite(ImageOps.mirror(gun).resize((128,96),LANCZOS),(12,0))
    carrier_palettes=sorted({c for room,key,c in r['observed'] if key==k}|{pal})
    for color in carrier_palettes:
        for y in [-8,0,8]:
            for x in [-24,-16,-8,0,8]:
                vk,vc=pack.virtual(k,color,x,y);sx=(x+24)*4;sy=(y+8)*4
                pack.tile(prefix,vk,vc,canon.crop((sx,sy,sx+32,sy+32)))
    rope=Image.new('RGBA',(32,32));d=ImageDraw.Draw(rope)
    for x,col in [(10,'#252b34'),(12,'#7a8d98'),(15,'#bbbec2'),(18,'#505862')]:d.line((x,0,x,32),fill=col,width=3)
    for y in range(-4,36,6):d.line((10,y+3,19,y),fill='#383e45',width=2)
    for x,y,key,c,h,v in rail:
        if key.startswith('1C141C'):art=rope
        elif key.startswith('FFFF18'):art=mount.resize((32,32),LANCZOS)
        else:art=CLEAR
        for color in sorted({oc for _,ok,oc in r['observed'] if ok==key}|{c}):pack.tile(prefix,key,color,art)
    mount=mount.resize((64,28),LANCZOS);plate=Image.new('RGBA',(64,32));plate.alpha_composite(mount,(0,0))
    for x,y,k,c,h,v in r['cable_mount']:
        if k.startswith('E0E0E0'):
            # Rope is at the outer edge of this native tile, underneath the reel.
            a=Image.new('RGBA',(32,32));a.alpha_composite(rope,(-10,0));pack.tile(NORMAL+'&a8Room39',k,c,a)
        else:
            sx=(128-x)*4;cell=plate.crop((sx,0,sx+32,32));pack.tile(NORMAL+'&a8Room39',k,c,cell)

def build(source,dest):
    assert source.resolve()!=dest.resolve()
    dest.mkdir(parents=True,exist_ok=True)
    for f in source.iterdir():
        if f.is_file():shutil.copy2(f,dest/f.name)
    pack=Pack(source);records=json.loads((DATA/'field.json').read_text());modules=json.loads((DATA/'modules.json').read_text())
    pack.condition('area8','memoryCheckConstant,004D,==,08')
    for name,r in [('a8Core',32),('a8RadioA',51),('a8RadioB',52),('a8Menu',108)]+[(f'a8Room{r}',r)for r in (7,38,39,77,78,79,80,81,82,83)]:
        pack.condition(name,f'memoryCheckConstant,004C,==,{r:02X}')
    records['new_actors']['observed']=records['sprites']
    new_actors(pack,records['new_actors']);
    first=len(pack.tiles);transplant(pack,records);pos=len(pack.tiles);parachutist(pack)
    pack.tiles[first:]=pack.tiles[pos:]+pack.tiles[first:pos]
    terrain(pack,records,modules)
    wall=Image.open(ART/'area8-machinery-wall.png').convert('RGB').resize((1024,960),LANCZOS)
    wall=ImageEnhance.Brightness(wall).enhance(.78);wall.save(dest/WALL)
    pack.finish(source,dest)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('dest',type=Path)
    args=p.parse_args();build(args.source,args.dest)
