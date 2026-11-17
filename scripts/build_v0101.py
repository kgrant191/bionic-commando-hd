"""Repair overhead assembly and scrolling town signs on the v0.10.0 build.

Only HD renderer rules change. Gameplay state and movie inputs remain live.
"""
from pathlib import Path
from collections import defaultdict
import argparse, hashlib, json, re, subprocess, sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NORMAL = '!title&!worldmap&!equipment&!radio&!areaClear'


def patch(dest):
    lines = (dest/'hires.txt').read_text().splitlines()
    images = [Image.open(dest/l[5:]).convert('RGBA') for l in lines if l.startswith('<img>')]
    idx = len(images)
    atlas = Image.new('RGBA', (2048, 4096))
    cells, rules, conds, additions = {}, [], [], []
    blank = Image.new('RGBA', (32,32))

    def emit(k, p, im, guard=None):
        assert im.size == (32,32)
        data = im.tobytes()
        if data not in cells:
            n = len(cells); xy = (n % 64 * 32, n // 64 * 32)
            assert xy[1] < atlas.height
            cells[data] = xy; atlas.paste(im, xy)
        x,y = cells[data]
        rules.append((f'[{guard}]' if guard else '') + f'<tile>{idx},{k},{p:08X},{x},{y},1,N')

    nearby = {}
    def near(dx,dy,k):
        key = dx,dy,k
        if key not in nearby:
            name = f'v0101Near{len(nearby)}'; nearby[key] = name
            conds.append(f'<condition>{name},spriteNearby,{dx},{dy},{k},FF202A0F,Y')
        return nearby[key]

    # Exactly one primary native anchor per direction. A nearby hair overlay
    # distinguishes Spencer from enemies that share his body CHR and hit colors.
    anchors = json.loads((ROOT/'capture/v0101/overhead-anchors.json').read_text())
    source = {name:Image.open(ROOT/'art'/filename).convert('RGBA') for name,filename in [
        ('Rocket','overhead-rocket-v0101.png'),('Wide','overhead-wide-v0100.png'),
        ('Starter','overhead-commandos-v081.png')]}
    diagonal=Image.open(ROOT/'art/overhead-front-diagonal-v0101.png').convert('RGBA')
    diagonal_wide=Image.open(ROOT/'art/overhead-wide-front-diagonal-v0101.png').convert('RGBA')
    actor_count = 0
    for rec in anchors:
        if not rec['parts']: continue
        head, cell = rec['head'], rec['cell']
        if head.startswith('58381B'): cell=2  # Down, verified with directional inputs.
        hair = sorted({(dx,dy,k) for dx,dy,k,p,h,v in rec['parts']
                       if -10 <= dy <= 0 and
                       sum(b.bit_count() for b in bytes.fromhex(k[:16])) <= 4 and
                       sum(b.bit_count() for b in bytes.fromhex(k[16:])) >= 18})
        assert hair, head
        actor_count += 1
        canvases = {}
        for weapon,sheet in source.items():
            cw,ch = sheet.width//4,sheet.height//2
            art = sheet.crop((cell*cw,0,(cell+1)*cw,ch))
            if head.startswith('0C38F0'):
                col={'Rocket':0,'Wide':1,'Starter':2}[weapon]
                dw=diagonal.width//3
                art=diagonal_wide.copy() if weapon=='Wide' else diagonal.crop((col*dw,0,(col+1)*dw,diagonal.height))
            a = np.array(art); a[a[:,:,3]<96] = 0; art = Image.fromarray(a)
            box = art.getchannel('A').getbbox(); assert box
            art = art.crop(box)
            # One fixed size for each facing, independent of walking stride,
            # flash palette and the varying native gun/tile bounds.
            height = 140 if weapon == 'Rocket' else 128
            width = round(art.width * height / art.height)
            art = art.resize((width,height),Image.Resampling.LANCZOS)
            canvas = Image.new('RGBA',(256,256))
            # Head anchors are eight native pixels below the sprite's top.
            # Keep the foot baseline constant; the large launcher may extend up.
            canvas.alpha_composite(art,(round(96+rec['cx']*4-width/2),192-height))
            canvases[weapon] = canvas
            pose_dir=ROOT/'validation/pose-previews/v0101';pose_dir.mkdir(parents=True,exist_ok=True)
            canvas.save(pose_dir/f'{head[:6]}-{weapon}.png')
        offsets = [(x,y) for y in range(-32,40,8) for x in range(-24,40,8)
                   if any(im.crop((96+x*4,96+y*4,128+x*4,128+y*4)).getchannel('A').getbbox()
                          for im in canvases.values())]
        for p in rec['palettes']:
            for x,y in offsets:
                virtual = hashlib.md5(f'BCHD:v0101:{head}:{x}:{y}'.encode()).hexdigest().upper()
                additions.append(f'<addition>{head},{p:08X},{x},{y},{virtual},{p:08X},N')
                for weapon,canvas in canvases.items():
                    im = canvas.crop((96+x*4,96+y*4,128+x*4,128+y*4))
                    if p != 0xFF202A0F:
                        a=np.array(im);a[:,:,:3]=np.clip(a[:,:,:3].astype(float)*[1.08,.82,.75],0,255).astype('uint8');im=Image.fromarray(a)
                    equip = 'weapon'+weapon if weapon != 'Starter' else '!weaponRocket&!weaponWide'
                    for dx,dy,k in hair:
                        for scene in ['interception','interception14']:
                            guard=f'{scene}&{NORMAL}&{equip}&'+near(dx-x,dy-y,k)
                            emit(virtual,p,im,guard)
                emit(virtual,p,blank)
            # Blank native components only when this player's anchor and hair
            # agree. Palette changes affect the complete pose, never its parts.
            pieces={(dx,dy,k,h,v) for dx,dy,k,pp,h,v in rec['parts']}
            pieces.add((0,0,head,0,0))
            for dx,dy,k,h,v in sorted(pieces):
                hs=-1 if h else 1; vs=-1 if v else 1
                for hx,hy,hk in hair:
                    guards=[near(-dx*hs,-dy*vs,head),near((hx-dx)*hs,(hy-dy)*vs,hk)]
                    for scene in ['interception','interception14']:
                        # Hair often keeps its red palette while the body flashes.
                        for pp in {p,0xFF36060F}:
                            emit(k,pp,blank,f'{scene}&{NORMAL}&'+'&'.join(guards))

    # The sign patterns already encode their position within the plaque.
    # Depending on a second tile makes them revert when that tile scrolls off
    # screen. Each plaque component therefore keeps its painted crop directly.
    sign_keys = set(); sign_rules = []
    for line in lines:
        if line.startswith('[area16&!townRoom') and '&townShield' in line:
            guard,body=line.split(']',1)
            guard=re.sub(r'&townShield\d+_\d+','',guard)
            sign_rules.append(guard+']'+body)
            sign_keys.add(body.split(',')[1])
    rules += list(dict.fromkeys(sign_rules))

    # The room contact is a bareheaded red-clothed man. Reuse the native
    # portrait's live mouth conditions/virtual cells, but select his own art.
    portrait = Image.open(ROOT/'art/area16-red-contact-portraits-v0101.png').convert('RGBA')
    expressions=[portrait.crop((i*portrait.width//2,0,(i+1)*portrait.width//2,portrait.height)).resize((192,256),Image.Resampling.LANCZOS) for i in range(2)]
    portrait_cells = {}
    for line in lines:
        if not line.startswith('<addition>'):continue
        a=line[10:].split(',')
        if a[0]=='FDDE2E1EFE1E0D0D7130104000E0F0F0' and a[1]=='FF263506':
            portrait_cells[a[4]] = (int(a[2])+24,int(a[3])+24)
    assert len(portrait_cells)==48
    portrait_rules=0
    for line in lines:
        if not line.startswith('[area16&') or '<tile>' not in line:continue
        guard,body=line.split(']',1);a=body[6:].split(',')
        if a[1] not in portrait_cells:continue
        x,y=portrait_cells[a[1]];talk=bool(re.search(r'&a13mouth\d+',guard))
        im=expressions[int(talk)].crop(((x+8)*4,y*4,(x+16)*4,(y+8)*4))
        emit(a[1],int(a[2],16),im,guard[1:]+'&townRoom');portrait_rules+=1
    assert portrait_rules==96
    # Prioritize the new definitions and overlays. Preserve all prior image
    # indices and runtime files for unrelated areas and the large round shot.
    insert=next(i for i,l in enumerate(lines) if '<tile>' in l)
    lines[insert:insert]=[f'<img>movement-town-v0101.png']+conds+list(dict.fromkeys(additions))+list(dict.fromkeys(rules))
    lines[0]='# Bionic Commando HD v0.10.1 - Stable movement, shoulder launcher and town fixes'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0,0,2048,((len(cells)+63)//64)*32)).save(dest/'movement-town-v0101.png')
    readme=(dest/'README.txt').read_text().replace('v0.10.0','v0.10.1')
    readme+='\nV0.10.1: Complete overhead Spencer poses across movement and hit flashes; large shoulder-fired rocket launcher; stable Area 16 building signs during scrolling; red-clothed contact retains his identity while talking.\n'
    (dest/'README.txt').write_text(readme)
    stats={'version':'0.10.1','primary_player_anchors':actor_count,'new_atlas_cells':len(cells),'new_rules':len(set(rules)),'new_additions':len(set(additions)),'scroll_stable_sign_patterns':len(sign_keys),'contact_portrait_rules':portrait_rules}
    (ROOT/'validation/v0101-build.json').write_text(json.dumps(stats,indent=2)+'\n')
    build=json.loads((ROOT/'build_stats.json').read_text());build.update(version='0.10.1',runtime_files=len(list(dest.iterdir())),tile_rules=sum('<tile>'in l for l in lines))
    (ROOT/'build_stats.json').write_text(json.dumps(build,indent=2)+'\n')
    print(json.dumps(stats,indent=2))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'pack');args=ap.parse_args()
    subprocess.run([sys.executable,str(ROOT/'scripts/build_v0100.py'),'--output',str(args.output)],check=True)
    patch(args.output)


if __name__=='__main__':main()
