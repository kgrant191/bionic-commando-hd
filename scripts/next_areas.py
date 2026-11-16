"""Intro and Areas 5/15; all runtime decisions use native state and tiles."""
import json
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import map_coordinates
from level_polish import fade_aliases
from poses import make_actor

def entries(root, movie, n):
    return [(int(a[0]),int(a[1]),int(a[2]),a[3],int(a[4]),int(a[5]),int(a[6]))
            for a in (l.split(',') for l in (root/f'capture/new-{movie}/{n:05}.tiles').read_text().splitlines())]

def font_tiles(root, indices, tile, scale):
    glyphs=json.loads((root/'capture/debrief-glyphs.json').read_text())
    shapes={np.packbits(indices(k)>0).tobytes():ch for k,ch in glyphs.items()}
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',40)
    def render(k,p):
        ink=indices(k)>0;ch=shapes.get(np.packbits(ink).tobytes())
        a=np.array(tile(k,p));a[~ink]=0
        if ch is None or ch in "',.-!?":return scale(Image.fromarray(a))
        im=Image.new('RGBA',(32,32))
        if ink.any():
            color=tuple(np.max(a[ink],axis=0));glyph=Image.new('RGBA',(64,64));ImageDraw.Draw(glyph).text((32,32),ch,font=font,anchor='mm',fill=color)
            box=glyph.getbbox()
            if box:im.alpha_composite(glyph.crop(box).resize((26,27),Image.Resampling.LANCZOS),(3,2))
        return im
    return render

def painted_tiles(root,movie,n,asset,indices,tile,warp=None):
    native=np.array(Image.open(root/f'capture/new-{movie}/{n:05}.png').convert('RGB'))
    art=Image.open(root/'art'/asset).convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
    if warp:
        xk,yk=warp;tx=np.interp(np.arange(1024)/4,*xk)*4;ty=np.interp(np.arange(960)/4,*yk)*4
        yy,xx=np.meshgrid(ty,tx,indexing='ij');a=np.array(art)
        art=Image.fromarray(np.stack([map_coordinates(a[:,:,c],[yy,xx],order=1,mode='nearest')for c in range(4)],2).astype('uint8'))
    locations={}
    for y in range(8,233):
        for x in range(249):locations.setdefault(native[y:y+8,x:x+8].tobytes(),(x,y))
    painted={};mapping={}
    for k,p in sorted({(e[3],e[4])for e in entries(root,movie,n)if e[0]==0}):
        if len(np.unique(indices(k)))<2:continue
        xy=locations.get(np.array(tile(k,p).convert('RGB')).tobytes())
        if xy is None:continue
        x,y=xy;im=art.crop((x*4,y*4,x*4+32,y*4+32))
        painted[k,p]=im;mapping[f'{k}:{p:08X}']=[movie,n,x,y,asset]
    return painted,mapping,art

def extend_next(root,keys,indices,tile,scale,rule,blank):
    conds=[
        '<condition>introMode,memoryCheckConstant,00CB,==,00',
        '<condition>introArea,memoryCheckConstant,004D,==,00',
        '<condition>storyActive,memoryCheckConstant,00CE,>=,01',
        '<condition>storyEnd,memoryCheckConstant,00CE,<=,04',
        '<condition>storyTop,positionCheckY,<,160',
        '<condition>area5,memoryCheckConstant,004D,==,05',
        '<condition>area15,memoryCheckConstant,004D,==,0F',
        '<condition>townRoom,memoryCheckConstant,004A,==,02',
        '<condition>interception,memoryCheckConstant,004C,==,13',
    ]
    backgrounds=[];stats={}
    story='introMode&introArea&storyActive&storyEnd&!title'
    font=font_tiles(root,indices,tile,scale)
    for scene,name in [(1,None),(2,'intro-dossier.png'),(3,'intro-headquarters.png'),(4,'intro-sunset.png')]:
        cn=f'storyScene{scene}';conds.append(f'<condition>{cn},memoryCheckConstant,00CE,==,{scene:02X}')
        canvas=Image.new('RGBA',(1024,960),(0,0,0,255))
        if name:
            art=Image.open(root/'art'/name).convert('RGBA')
            if scene==2:
                a=np.array(art);mask=np.max(a[:,:,:3],axis=2)>25;ys,xs=np.where(mask)
                art=art.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1)).resize((384,512),Image.Resampling.LANCZOS)
                canvas.paste(art,(320,64))
            else:canvas.paste(art.resize((1024,640),Image.Resampling.LANCZOS),(0,0))
        # The foreground illustration covers every old scenery pixel.
        canvas.save(root/f'pack/story-base-{scene}.png')
        backgrounds.append(f'[{story}&{cn}&screenEnabled]<background>story-base-{scene}.png,1,0,0,10')
        canvas.paste((0,0,0,0),(0,640,1024,960))
        canvas.save(root/f'pack/story-{scene}.png')
        backgrounds.append(f'[{story}&{cn}&screenEnabled]<background>story-{scene}.png,1,0,0,20')
    intro_pairs={(k,int(p,16)) for k,p in json.loads((root/'capture/new-intro/extra-keys.json').read_text())}
    for line in (root/'capture/new-intro/original-rules.txt').read_text().splitlines():
        if line.startswith('<tile>'):
            fields=line[6:].split(',');intro_pairs.add((fields[1],int(fields[2],16)))
    for k,p in keys:
        if p>>24!=255 and (k,p) in intro_pairs:
            rule(k,p,blank,story+'&storyTop')
            rule(k,p,font(k,p),story+'&!storyTop')
    # This illustration has three native palettes. Replace every component,
    # including skin and the rifle, directly so no old extremities remain.
    joe=[e for e in entries(root,'intro',3000) if e[0]==1 and e[3]!='0'*32]
    x0=min(e[1] for e in joe);y0=min(e[2] for e in joe);x1=max(e[1] for e in joe)+8;y1=max(e[2] for e in joe)+8
    sheet=Image.open(root/'art/super-joe.png').convert('RGBA');cw=sheet.width//3
    art=sheet.crop((cw,0,cw*2,sheet.height));art=art.crop(art.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()).resize(((x1-x0)*4,(y1-y0)*4),Image.Resampling.LANCZOS)
    for _,x,y,k,p,h,v in joe:
        im=art.crop(((x-x0)*4,(y-y0)*4,(x-x0+8)*4,(y-y0+8)*4))
        rule(k,p,im,story+'&storyScene4')

    normal='!title&!worldmap&!equipment&!radio&!areaClear'
    # Each family is scoped so shared patterns cannot repaint earlier areas.
    specs=[('5',2280,'area5-factory.png','area5&'+normal,
            (([0,40,128,144,200,256],[0,43,137,153,202,256]),([0,16,84,160,176,208,224,240],[0,18,82,162,179,210,228,240]))),
           ('5',1560,'area5-hazards.png','area5&'+normal,None),
           ('5',6840,'area5-shaft.png','area5&'+normal,None),
           ('5',21360,'area5-reactor.png','area5&'+normal,None),
           ('15',4920,'area15-room.png','area15&townRoom&'+normal,None),
           ('15',1080,'interception-terrain.png','interception&'+normal,None)]
    families={};mapping={}
    for movie,n,asset,guard,warp in specs:
        paint,m,art=painted_tiles(root,movie,n,asset,indices,tile,warp)
        family=families.setdefault(guard,{})
        for kp,im in paint.items():
            if kp not in family:family[kp]=im;mapping[f'{guard}:{kp[0]}:{kp[1]:08X}']=m[f'{kp[0]}:{kp[1]:08X}']
        if movie=='5'and n==2280:
            plaster=art.crop((264,464,296,496));olive=art.crop((620,100,652,132))
            for k,p in keys:
                ix=indices(k)
                if p==0x0F261000 and np.all(ix==2):family[k,p]=plaster
                if p==0x0F271807 and len(np.unique(ix))==1 and np.any(ix):family[k,p]=olive
        if movie=='5'and n==6840:
            wall=art.crop((40,360,72,392));wa=np.array(wall,float)
            # A single flat-field swatch tiles without disconnected panel seams.
            yy,xx=np.mgrid[:32,:32];w=(np.sin(np.pi*xx/31)*np.sin(np.pi*yy/31))[:,:,None]
            center=wa[:,:,:3].mean((0,1));wa[:,:,:3]=center+(wa[:,:,:3]-center)*w*.4
            wall=Image.fromarray(np.uint8(wa))
            for k,p in keys:
                if p==0x0F261606 and len(np.unique(indices(k)))==1 and np.any(indices(k)):family[k,p]=wall
        if movie=='15'and n==4920:
            for kp,im in list(family.items()):
                k,p=kp;ix=indices(k)
                # The room's voids and slopes retain their native collision silhouette.
                if np.any(ix==0):
                    ar=np.array(im);ar[np.repeat(np.repeat(ix==0,4,0),4,1)]=[0,0,0,255];family[kp]=Image.fromarray(ar)
            family['0'*32,0x0F201000]=Image.new('RGBA',(32,32),(0,0,0,255))
    factory=families['area5&'+normal]
    # The opposite-facing chain and rail cells use mirrored CHR data rather
    # than a hardware flip flag. Mirror the matching painted tile once.
    for (k,p),im in list(factory.items()):
        raw=np.frombuffer(bytes.fromhex(k),dtype=np.uint8)
        kh=bytes(int(f'{v:08b}'[::-1],2)for v in raw).hex().upper()
        factory.setdefault((kh,p),ImageOps.mirror(im))
    frame=Image.open(root/'art/exterior-doorframe-v076.png').convert('RGBA')
    header=frame.crop((0,0,frame.width,frame.height//4)).resize((128,32),Image.Resampling.LANCZOS)
    for ly,x,y,k,p,h,v in entries(root,'5',11640):
        if ly==0 and y==130 and 198<=x<230:
            factory[k,p]=header.crop(((x-198)*4,0,(x-190)*4,32))
    # Small fixed ceiling machinery: painted steel platform and vent below it.
    lift=Image.open(root/'art/cave-lift-v5.png').convert('RGBA').resize((1024,896),Image.Resampling.LANCZOS)
    mechanism=lift.crop((240,356,432,468)).resize((128,64),Image.Resampling.LANCZOS)
    for ly,x,y,k,p,h,v in entries(root,'5',17400):
        if ly==0 and 152<=x<184 and 15<=y<31:
            factory[k,p]=mechanism.crop(((x-152)*4,(y-15)*4,(x-144)*4,(y-7)*4))
    for guard,paint in families.items():
        fades=fade_aliases(paint)
        for k,p in keys:
            if p>>24==255:continue
            im=paint.get((k,p))
            if im is None and(k,p)in fades:
                base,factor=fades[k,p];ar=np.array(paint[k,base]);ar[:,:,:3]=(ar[:,:,:3].astype(float)*factor).astype('uint8');im=Image.fromarray(ar)
            if im is not None:rule(k,p,im,guard)
        stats[guard]=len(paint)
    # The supply chest is an OAM object; its four mirrored component patterns
    # must be painted separately from the room's background tiles.
    room=Image.open(root/'art/area15-room.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
    seen_chest=set()
    for ly,x,y,k,p,h,v in entries(root,'15',4920):
        if ly!=1 or not(158<=x<190 and 145<=y<161) or k in seen_chest:continue
        seen_chest.add(k);im=room.crop((x*4,y*4,(x+8)*4,(y+8)*4))
        if h:im=ImageOps.mirror(im)
        a=np.array(im);a[np.repeat(np.repeat(indices(k)==0,4,0),4,1),3]=0
        rule(k,p,Image.fromarray(a),'area15&townRoom&'+normal)
    # Shield acrobats: native head and pose signatures select the paintings.
    c,a,_=make_actor(root,keys,lambda k,p,im,g=None:rule(k,p,im,'area5&'+normal+'&'+g if g else None),blank,'blue',1,0xFF30210F)
    conds+=c;backgrounds+=a
    # Compact blue pose uses mirrored native halves, independent of a head anchor.
    curled=Image.open(root/'art/blue-curled.png').convert('RGBA');curled=curled.crop(curled.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()).resize((64,64),Image.Resampling.LANCZOS)
    for k,x,y in [('FFFFFEF8FCCC5ECC2445FE18244CD2CC',32,0),('1F0FBFBF05FC0300140C4440FEFF0300',0,32)]:
        for kk,p in keys:
            if kk==k and p>>24==255:rule(k,p,curled.crop((x,y,x+32,y+32)),'area5&'+normal)
    # The brief overhead hit puff flashes through two palettes at one position.
    effects=Image.open(root/'art/effects-v5.png').convert('RGBA');small=effects.crop((0,0,round(effects.width*510/2208),effects.height));small=small.crop(small.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()).resize((64,32),Image.Resampling.LANCZOS)
    for k,p in keys:
        if k=='FFFF7F5F3D0B0601048672603E0E0701' and p>>24==255:rule(k,p,small.crop((0,0,32,32)),'interception&'+normal)
    # Top-down figures use direct component replacements; no extra sprite layer.
    for actor,palette in [('overhead-green',0xFF202A0F),('overhead-red',0xFF36150F)]:
        records=json.loads((root/f'capture/{actor}-poses.json').read_text());sheet=Image.open(root/'art/interception-soldiers.png').convert('RGBA');cw,ch=sheet.width//4,sheet.height//2
        seen=set();fallback={}
        for rec in sorted(records,key=lambda r:-r['count']):
            parts=[(0,0,rec['head'],0,0)]+rec['parts'];x0=min(t[0]for t in parts);y0=min(t[1]for t in parts);x1=max(t[0]for t in parts)+8;y1=max(t[1]for t in parts)+8
            cell=rec['cell'];art=sheet.crop((cell%4*cw,cell//4*ch,(cell%4+1)*cw,(cell//4+1)*ch));box=art.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox();art=art.crop(box).resize(((x1-x0)*4,(y1-y0)*4),Image.Resampling.LANCZOS)
            for dx,dy,k,h,v in parts:
                sig=(dx,dy,k,h,v,rec['head'])
                if sig in seen:continue
                seen.add(sig);hs=-1 if h else 1;vs=-1 if v else 1
                cn=f'topdownPart{len(conds)}';conds.append(f'<condition>{cn},spriteNearby,{-dx*hs},{-dy*vs},{rec["head"]},{palette:08X},N')
                im=art.crop(((dx-x0)*4,(dy-y0)*4,(dx-x0+8)*4,(dy-y0+8)*4))
                if h:im=ImageOps.mirror(im)
                if v:im=ImageOps.flip(im)
                rule(k,palette,im,'interception&'+normal+'&'+cn)
                fallback.setdefault(k,im)
        for k,im in fallback.items():rule(k,palette,im,'interception&'+normal)
        stats[actor]=len(records)
    (root/'validation/intro-areas5-15-mapping.json').write_text(json.dumps({'painted_families':stats,'mapping':mapping},indent=2)+'\n')
    return conds,backgrounds
