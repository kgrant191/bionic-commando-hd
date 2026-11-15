"""Painted metasprites attached to live CHR-RAM anchors, with local pose tests."""
import hashlib,itertools,json
from PIL import Image
import numpy as np
from level_polish import fade_palette
HEAD='000102F17A797A7E52FFFE8F7E67064E'

def make_actor(root,keys,rule,blank,actor,rows,normal_palette):
    records=json.loads((root/f'capture/{actor}-poses.json').read_text())
    for rec in records:rec.setdefault('head',HEAD)
    default=root/f'art/{actor}-poses-v{4 if actor=="spencer" else 3}.png'
    src=Image.open(default if default.exists() else root/'art'/records[0].get('asset','area13-npcs.png')).convert('RGBA')
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
        sheet=Image.open(root/'art'/rec['asset']).convert('RGBA')if 'asset'in rec else src
        columns=rec.get('columns',4);cell=rec['cell'];cw=sheet.width//columns;ch=sheet.height//rec.get('rows',rows)
        art=sheet.crop((cell%columns*cw,cell//columns*ch,(cell%columns+1)*cw,(cell//columns+1)*ch))
        if rec.get('alpha_cutoff'):
            aa=np.array(art);aa[aa[:,:,3]<rec['alpha_cutoff'],3]=0;art=Image.fromarray(aa)
        if rec.get('mirror_art'):art=ImageOps.mirror(art)
        # Remove very faint isolated matte pixels from the bounding calculation
        # only; keep the generated alpha in the actual art.
        ab=art.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox();assert ab
        canvas=Image.new('RGBA',(96*4,80*4))
        if actor=='enemy':
            # One pixels-per-body scale across the sheet; weapon length no
            # longer enlarges a standing soldier relative to his crouch pose.
            factor=152/cw
            top=np.array(art.getchannel('A'))>64
            band=top[ab[1]:ab[1]+int(ch*.1)]
            xs=np.where(band)[1]
            head_x=float(np.median(xs))if len(xs)else cw/2
            if rec['cell']==5:head_x=cw*.49 # Raised grenade is above the helmet.
            dx=round(44*4+(ab[0]-head_x)*factor)
            dy=round(y1*4-(ab[3]-ab[1])*factor)
            art=art.crop(ab).resize((round((ab[2]-ab[0])*factor),round((ab[3]-ab[1])*factor)),Image.Resampling.LANCZOS)
            canvas.alpha_composite(art,(dx,dy))
        elif actor in {'area4','a13trooper','neutral'}:
            # Keep one body scale across an animation sheet. Native stride
            # widths vary; fitting every pose into that width inflated torsos.
            ref=sheet.crop((0,0,cw,ch))
            rb=ref.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
            factor=128/(rb[3]-rb[1])
            band=np.array(art.getchannel('A'))[ab[1]:ab[1]+round(ch*.12)]>64
            xs=np.where(band)[1]
            head_x=float(np.median(xs)) if len(xs) else (ab[0]+ab[2])/2
            dx=round(44*4+(ab[0]-head_x)*factor)
            dy=24*4
            art=art.crop(ab).resize((round((ab[2]-ab[0])*factor),round((ab[3]-ab[1])*factor)),Image.Resampling.LANCZOS)
            canvas.alpha_composite(art,(dx,dy))
        elif actor=='contact' and not rec.get('fit_native_bounds'):
            art=art.crop(ab);height=(y1-y0)*4
            width=round(art.width*height/art.height)
            art=art.resize((width,height),Image.Resampling.LANCZOS)
            canvas.alpha_composite(art,(round((x0+x1)*2-width/2),y0*4))
        else:
            art=art.crop(ab).resize(((x1-x0)*4,(y1-y0)*4),Image.Resampling.LANCZOS)
            canvas.alpha_composite(art,(x0*4,y0*4))
        pose_dir=root/'validation/pose-previews'/actor;pose_dir.mkdir(parents=True,exist_ok=True)
        canvas.save(pose_dir/f"{rec['id']}.png")
        images[rec['id']]=canvas
        stats.append({'id':rec['id'],'head':rec['head'],'cell':cell,'native_bounds':bbox,'signature':[list(t)for t in signature],'sample_frames':len(rec['frames'])})
    families={}
    for rec in records:
        family=tuple(sorted({t[2]for t in rec['parts']}|{rec['head']}))
        if family in families:images[rec['id']]=images[families[family]]
        else:families[family]=rec['id']
    # Native head anchors carry direction/visibility; virtual tiles inherit the
    # same OAM flip/priority. No ROM, RAM or animation values are changed.
    def palette_pose(im,hp):
        if hp!=normal_palette:
            a=np.array(im);a[:,:,:3]=np.clip(a[:,:,:3].astype(float)*([1.1,1.1,1.1] if actor=='area13' else [1.15,.72,.65]),0,255);im=Image.fromarray(a)
        fade=next((step for base in (normal_palette,0xFF202A0F,0xFF30160F)
                   for step in range(1,5) if fade_palette(base,step)==hp),0)
        if hp==0xFF0F0F0F:fade=4
        if fade:
            a=np.array(im);a[:,:,:3]=(a[:,:,:3].astype(float)*[1,.62,.32,.12,0][fade]).astype('uint8');im=Image.fromarray(a)
        return im
    offset_groups={}
    for head in sorted({r['head']for r in records}):
        group=[r for r in records if r['head']==head]
        partial=max(group,key=lambda r:r['count'])
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
                    rule(vkey,hp,palette_pose(im,hp),pose_guard(rec,x,y))
                # Visible-body signatures can disappear during OAM overlap or
                # screen clipping. A live head still identifies the actor.
                # Keep its most common painted pose until the full signature
                # becomes visible; never expose native fragments in between.
                im=images[partial['id']].crop(((40+x)*4,(24+y)*4,(48+x)*4,(32+y)*4))
                rule(vkey,hp,palette_pose(im,hp),'!title')
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
    # Hide a partial actor's surviving native pieces using the same local head
    # relationship. The pattern, offset and head must agree; unrelated bullets
    # and nearby soldiers are not globally blanked.
    for rec in records:
        for dx,dy,k,h,v in [(0,0,rec['head'],0,0)]+rec['parts']:
            hs=-1 if h else 1;vs=-1 if v else 1
            guard='!title' if k==rec['head'] else '!title&'+condition(-dx*hs,-dy*vs,rec['head'],normal_palette,True)
            for p in sorted(keypal.get(k,[])):
                t=(k,p,guard)
                if t in hidden:continue
                hidden.add(t);rule(k,p,blank,guard)
    if actor in {'enemy','area4','a13trooper'}:
        # If another sprite completely covers the head, no head addition can
        # be emitted. Preserve the surviving limb's occlusion with a crop of
        # the painted pose, rather than reverting to a material-tinted NES limb.
        # Shared Spencer and projectile patterns are deliberately excluded.
        spencer=json.loads((root/'capture/spencer-poses.json').read_text())
        shared={r.get('head',HEAD)for r in spencer}|{t[2]for r in spencer for t in r['parts']}
        fragments=set()
        for rec in records:
            for dx,dy,k,h,v in rec['parts']:
                if k in shared or k in fragments or k in offset_groups:continue
                fragments.add(k)
                im=images[rec['id']].crop(((40+dx)*4,(24+dy)*4,(48+dx)*4,(32+dy)*4))
                if h:im=ImageOps.mirror(im)
                if v:im=ImageOps.flip(im)
                a=np.array(im);solid=np.repeat(np.repeat(pattern(k)>0,4,0),4,1)
                a[~solid,3]=0;im=Image.fromarray(a)
                for p in sorted(keypal.get(k,[])):
                    rule(k,p,palette_pose(im,p),'!title')
    (root/f'validation/{actor}_pose_mapping.json').write_text(json.dumps({'poses':stats,'virtual_offsets':offset_groups,'virtual_keys':[[k,f'{p:08X}']for k,p in virtual]},indent=2)+'\n')
    return conds,additions,virtual

def make_poses(root,keys,rule,blank):
    result=[[],[],[]]
    for actor,rows,palette in [('spencer',4,0xFF36060F),('enemy',3,0xFF36150F)]:
        emit=rule if actor=='spencer' else lambda k,p,im,g=None:rule(k,p,im,'!area13&'+g if g is not None else None)
        for out,items in zip(result,make_actor(root,keys,emit,blank,actor,rows,palette)):out.extend(items)
    return result
