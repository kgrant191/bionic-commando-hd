"""Painted metasprites attached to live CHR-RAM anchors, with local pose tests."""
import hashlib,itertools,json
from PIL import Image
import numpy as np
HEAD='000102F17A797A7E52FFFE8F7E67064E'

def make_actor(root,keys,rule,blank,actor,rows,normal_palette):
    records=json.loads((root/f'capture/{actor}-poses.json').read_text())
    for rec in records:rec.setdefault('head',HEAD)
    src=Image.open(root/f'art/{actor}-poses-v3.png').convert('RGBA')
    assert src.getchannel('A').getextrema()[0]==0,'Painted sprites need genuine alpha'
    records.sort(key=lambda r:(-len({t[2]for t in r['parts']}),-r['count']))
    keypal={}
    for k,p in keys:
        if p>>24==255:keypal.setdefault(k,set()).add(p)
    conds=[];additions=[];condition_cache={};virtual=[];images={};stats=[]
    def condition(dx,dy,k,p=0xFF202A0F,ignore=True):
        t=(dx,dy,k,p,ignore)
        if t not in condition_cache:
            name=f'{actor}Pose{len(condition_cache)}';condition_cache[t]=name
            conds.append(f'<condition>{name},spriteNearby,{dx},{dy},{k},{p:08X},{"Y"if ignore else"N"}')
        return condition_cache[t]
    def pose_guard(rec,ox,oy,hs=1,vs=1):
        return '&'.join(['!title']+[condition((t[0]-ox)*hs,(t[1]-oy)*vs,t[2])for t in rec['signature']])
    # Positive signatures distinguish native poses; more complete supersets
    # (e.g. parachute cords) take priority over the plain standing pose.
    for rec in records:
        own={tuple(t)for t in rec['parts']}|{(0,0,rec['head'],0,0)}
        own_keys={t[2]for t in own}
        others=[{t[2]for t in r['parts']}|{r['head']}for r in records if r is not rec and r['head']==rec['head']]
        others=[s for s in others if not own_keys<=s]
        ranked=sorted(own,key=lambda t:(t[1]<8,-sum(b.bit_count()for b in bytes.fromhex(t[2])),abs(t[0])))
        signature=None
        for size in [1,2,3,4]:
            for combo in itertools.combinations(ranked,size):
                if all(not {t[2]for t in combo}<=o for o in others):signature=combo;break
            if signature:break
        if signature is None:signature=tuple(ranked)
        rec['signature']=signature
        # Reconstruct the original opaque bounds at 4x, preserving native gun,
        # hand and foot endpoints rather than stretching to a generic pose box.
        from PIL import ImageOps
        def pattern(k):
            bits=np.unpackbits(np.frombuffer(bytes.fromhex(k),dtype=np.uint8)).reshape(16,8)
            return bits[:8]+2*bits[8:]
        mask=Image.new('L',(96,80))
        for dx,dy,k,h,v in [(0,0,rec['head'],0,0)]+rec['parts']:
            a=Image.fromarray((pattern(k)>0).astype('uint8')*255)
            if h:a=ImageOps.mirror(a)
            if v:a=ImageOps.flip(a)
            mask.paste(a,(40+dx,24+dy),a)
        bbox=mask.getbbox();x0,y0,x1,y1=bbox
        cell=rec['cell'];cw=src.width//4;ch=src.height//rows
        art=src.crop((cell%4*cw,cell//4*ch,(cell%4+1)*cw,(cell//4+1)*ch))
        # Remove very faint isolated matte pixels from the bounding calculation
        # only; keep the generated alpha in the actual art.
        ab=art.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox();assert ab
        art=art.crop(ab).resize(((x1-x0)*4,(y1-y0)*4),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(96*4,80*4));canvas.alpha_composite(art,(x0*4,y0*4));images[rec['id']]=canvas
        stats.append({'id':rec['id'],'head':rec['head'],'cell':cell,'native_bounds':bbox,'signature':[list(t)for t in signature],'sample_frames':len(rec['frames'])})
    families={}
    for rec in records:
        family=tuple(sorted({t[2]for t in rec['parts']}|{rec['head']}))
        if family in families:images[rec['id']]=images[families[family]]
        else:families[family]=rec['id']
    # Native head anchors carry direction/visibility; virtual tiles inherit the
    # same OAM flip/priority. No ROM, RAM or animation values are changed.
    offset_groups={}
    for head in sorted({r['head']for r in records}):
        group=[r for r in records if r['head']==head]
        offsets=[]
        for y in range(-24,56,8):
            for x in range(-40,56,8):
                box=((40+x)*4,(24+y)*4,(48+x)*4,(32+y)*4)
                if any(images[r['id']].crop(box).getchannel('A').getbbox()for r in group):offsets.append((x,y))
        offset_groups[head]=offsets
        for x,y in offsets:
            vkey=hashlib.md5(f'BionicCommandoHD:{actor}:{head}:{x}:{y}'.encode()).hexdigest().upper()
            assert all(k!=vkey for k,p in keys)
            for hp in sorted(keypal[head]):
                additions.append(f'<addition>{head},{hp:08X},{x},{y},{vkey},{hp:08X},N')
                virtual.append((vkey,hp))
                for rec in group:
                    im=images[rec['id']].crop(((40+x)*4,(24+y)*4,(48+x)*4,(32+y)*4))
                    # Explicit blank cells prevent a less-specific pose from
                    # leaking through a selected pose's transparent areas.
                    if hp!=normal_palette:
                        a=np.array(im);a[:,:,:3]=np.clip(a[:,:,:3].astype(float)*[1.15,.72,.65],0,255);im=Image.fromarray(a)
                    rule(vkey,hp,im,pose_guard(rec,x,y))
                rule(vkey,hp,blank)
    # Suppress exactly the original components belonging to each recognized
    # figure. The head test prevents shared enemy/projectile patterns vanishing.
    hidden=set()
    for rec in records:
        for dx,dy,k,h,v in [(0,0,rec['head'],0,0)]+rec['parts']:
            hs=-1 if h else 1;vs=-1 if v else 1
            guard=pose_guard(rec,dx,dy,hs,vs)
            if k!=rec['head']:guard+='&'+condition(-dx*hs,-dy*vs,rec['head'],normal_palette,True)
            for p in sorted(keypal.get(k,[])):
                t=(k,p,guard)
                if t in hidden:continue
                hidden.add(t);rule(k,p,blank,guard)
    (root/f'validation/{actor}_pose_mapping.json').write_text(json.dumps({'poses':stats,'virtual_offsets':offset_groups,'virtual_keys':[[k,f'{p:08X}']for k,p in virtual]},indent=2)+'\n')
    return conds,additions,virtual

def make_poses(root,keys,rule,blank):
    result=[[],[],[]]
    for actor,rows,palette in [('spencer',4,0xFF36060F),('enemy',3,0xFF36150F)]:
        for out,items in zip(result,make_actor(root,keys,rule,blank,actor,rows,palette)):out.extend(items)
    return result
