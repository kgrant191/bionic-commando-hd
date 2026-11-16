"""Verify the focused Super Joe fix against a v0.8.1 pack and replay."""
from pathlib import Path
from collections import defaultdict
import argparse, hashlib, json
import numpy as np
from PIL import Image

p=argparse.ArgumentParser()
p.add_argument('--previous-pack',type=Path,required=True)
p.add_argument('--previous-frames',type=Path,required=True)
p.add_argument('--frames',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1]
def rules(pack):
    atlas=Image.open(pack/'tiles.png').convert('RGBA');out=defaultdict(list);cache={}
    for line in (pack/'hires.txt').read_text().splitlines():
        if '<tile>' not in line:continue
        guard,body=line.split('<tile>');v=body.split(',');xy=tuple(map(int,v[3:5]))
        if xy not in cache:
            x,y=xy;cache[xy]=hashlib.sha256(atlas.crop((x,y,x+32,y+32)).tobytes()).hexdigest()
        out[v[1],v[2]].append((guard,cache[xy],tuple(v[5:])))
    return out
old,new=rules(a.previous_pack),rules(root/'pack')
assert all(new[k]==v for k,v in old.items()),'An existing tile rendering changed'
extra=set(new)-set(old)
virtual={hashlib.md5(f'super-joe-complete:0:{dy}'.encode()).hexdigest().upper() for dy in (24,32,40)}
assert {k for k,pal in extra}==virtual
for f in a.previous_pack.glob('*.png'):
    if f.name!='tiles.png':assert f.read_bytes()==(root/'pack'/f.name).read_bytes(),f.name
before_lines=set((a.previous_pack/'hires.txt').read_text().splitlines())
after_lines=set((root/'pack/hires.txt').read_text().splitlines())
old_add={x for x in before_lines if x.startswith('<addition>')}
new_add={x for x in after_lines if x.startswith('<addition>')}
assert old_add<=new_add
assert len(new_add-old_add)==len(extra)
assert {x for x in before_lines if '<condition>' in x}=={x for x in after_lines if '<condition>' in x}

sheet=Image.open(root/'art/super-joe.png').convert('RGBA');cw=sheet.width//3
art=sheet.crop((cw,0,cw*2,sheet.height));art=art.crop(art.getchannel('A').point(lambda x:255 if x>32 else 0).getbbox()).resize((128,192),Image.Resampling.LANCZOS)
mask=np.zeros((896,1024),bool);mask[420:516,576:608]=True
checked=[];visible=[];max_error=0
for f in sorted(a.frames.glob('*.png')):
    prior=a.previous_frames/f.name
    if f.stat().st_size<100 or not prior.exists() or prior.stat().st_size<100:continue
    before=Image.open(prior).convert('RGBA');actual=Image.open(f).convert('RGBA')
    b,n=np.array(before),np.array(actual)
    assert np.array_equal(b[~mask],n[~mask]),f'Unrelated pixels changed in {f.name}'
    changed=not np.array_equal(b,n)
    if changed:
        for dy in (24,32,40):
            before.alpha_composite(art.crop((0,dy*4,32,dy*4+32)),(576,(89+dy-8)*4))
        error=int(np.abs(np.array(before).astype(int)-n.astype(int)).max())
        max_error=max(max_error,error)
        assert error<=2,(f.name,error)
        visible.append(int(f.stem))
    checked.append(int(f.stem))
assert 3000 in visible and 3360 in visible
report={'version':'0.8.2','missing_native_cells':[[144,113],[144,121],[144,129]],
        'new_virtual_tile_palette_pairs':len(extra),'new_sprite_additions':len(new_add-old_add),
        'all_existing_tile_renderings_unchanged':True,'all_background_images_unchanged':True,
        'compared_frames':checked,'frames_with_complete_rear_leg':visible,
        'maximum_channel_error_against_complete_source_composite':max_error,
        'outside_rear_leg_pixels_unchanged':True}
(root/'validation/super-joe-v082.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(checked),'frame comparisons;',len(visible),'complete rear-leg samples;',len(extra),'new tile/palette pieces')
