"""Weapon-specific art, observed palette repairs, and Area 16 coverage.

Rebuilds from the preserved, hash-verified v0.9.8 runtime. No gameplay writes.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
from poses import make_actor
ROOT=Path(__file__).resolve().parents[1]
NORMAL='!title&!worldmap&!equipment&!radio&!areaClear'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);ap.add_argument('--output',type=Path,default=ROOT/'pack');args=ap.parse_args()
 with tempfile.TemporaryDirectory(prefix='bionic-v0100-') as td:
  temp=Path(td);base=args.baseline
  if base is None:
   base=ROOT/'baselines/v098'
  expected=json.loads((ROOT/'baselines/v098.json').read_text())['files']
  assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in base.iterdir()if p.is_file()}==expected,'Unexpected v0.9.8 baseline'
  dest=args.output;dest.mkdir(exist_ok=True,parents=True);shutil.copytree(base,dest,dirs_exist_ok=True)
  lines=(base/'hires.txt').read_text().splitlines()
  lines.insert(5,'<condition>interception14,memoryCheckConstant,004C,==,14')
  images=[Image.open(base/l[5:]).convert('RGBA')for l in lines if l.startswith('<img>')]
  atlas=Image.new('RGBA',(2048,8192));cells={};idx=len(images);rules=[];conds=[];adds=[];bgs=[]
  blank=Image.new('RGBA',(32,32))
  def place(im):
   assert im.size==(32,32)
   b=im.tobytes()
   if b not in cells:
    n=len(cells);x=n%64*32;y=n//64*32;assert y<8192;atlas.paste(im,(x,y));cells[b]=(x,y)
   return cells[b]
  def emit(k,p,im,g=None):
   x,y=place(im);rules.append((f'[{g}]'if g else'')+f'<tile>{idx},{k},{p:08X},{x},{y},1,N')
  def parse(l):
   g,a=l.split('<tile>',1);return g,a.split(',')
  def crop(a):
   x,y=map(int,a[3:5]);return images[int(a[0])].crop((x,y,x+32,y+32))
  def entries(name,n):
   return [(int(l),int(x),int(y),k,int(p),int(h),int(v))for l,x,y,k,p,h,v in(l.split(',')for l in(ROOT/f'capture/v0100/{name}-{n:05}.tiles').read_text().splitlines())]
  def clean(im):
   a=np.array(im.convert('RGBA'));a[a[:,:,3]<96]=0;return Image.fromarray(a)
  def fit(im,size):
   im=clean(im);b=im.getchannel('A').getbbox();assert b;return im.crop(b).resize(size,Image.Resampling.LANCZOS)
  by=defaultdict(list);keypal=defaultdict(set);addby=defaultdict(list);virtual=set()
  for l in lines:
   if '<tile>'in l:
    g,a=parse(l);k,p=a[1],int(a[2],16);by[k,p].append(l);keypal[k].add(p)
   elif l.startswith('<addition>'):
    a=l[10:].split(',');addby[a[0],int(a[1],16)].append(a);virtual.add(a[4])
  observed={(k,int(p,16))for k,p in json.loads((ROOT/'capture/v0100/observed-keys.json').read_text())}
  keys={(k,p)for k,ps in keypal.items()if k not in virtual for p in ps}|observed
  for k,p in observed:keypal[k].add(p)
  conds+=['<condition>area16,memoryCheckConstant,004D,==,10',
          '<condition>weaponWide,memoryCheckConstant,04CA,==,02',
          '<condition>weaponRocket,memoryCheckConstant,04CA,==,01']
  # Match the original's 16x16 inventory cells and keep selection live.
  weapon=Image.open(ROOT/'art/weapons-v0100.png').convert('RGBA');cw=weapon.width//3
  icons=[fit(weapon.crop((i*cw,0,(i+1)*cw,weapon.height)),(64,64))for i in range(2)]
  menu=entries('issue1-enemy',1)
  for i,(ox,oy)in enumerate([(32,193),(144,73)]):
   for ly,x,y,k,p,h,v in menu:
    if ly==1 and ox<=x<ox+16 and oy<=y<oy+16:
     im=icons[i].crop(((x-ox)*4,(y-oy)*4,(x-ox+8)*4,(y-oy+8)*4))
     if h:im=ImageOps.mirror(im)
     for pp in sorted(keypal[k]):
      if pp>>24==255:emit(k,pp,im,'equipment')
  # Round rocket projectile and its separate ground shadow retain native cells.
  orb=fit(weapon.crop((cw*2,0,weapon.width,weapon.height)),(32,32))
  shadow=Image.new('RGBA',(32,32));ImageDraw.Draw(shadow).ellipse((0,12,31,20),fill=(12,16,18,170))
  for k,im in [('00183C6600663C1818664299FF994266',orb),('0000003CFFFF3C001800003CFFFF3C00',shadow)]:
   for p in sorted({p for kk,p in keys if kk==k}|{0xFF202A0F,0xFF202015,0xFF302A0F}):emit(k,p,im,NORMAL)
  # Side-view rocket is a four-quarter 16x16 shot. Its observed amber/red and
  # alarm palettes are distinct from the green/blue POW orbit palettes.
  side_orb=fit(weapon.crop((cw*2,0,weapon.width,weapon.height)),(64,64))
  for p in [0xFF30270F,0xFF36060F,0xFF36300F,0xFF36150F]:
   emit('0000020E16183800000121110907077F',p,side_orb.crop((0,0,32,32)),'weaponRocket&!interception&'+NORMAL)
  # Dropped overhead grenade: two native tiles, not a projectile or enemy limb.
  grenade=fit(Image.open(ROOT/'art/grenade-v076.png'),(32,52));canvas=Image.new('RGBA',(32,64));canvas.alpha_composite(grenade,(0,6))
  for j,k in enumerate(['0000000002070B170000000000387FFE','2B56A87000000000FEFCF87000000000']):
   for p in sorted(keypal[k]):
    if p>>24==255:emit(k,p,canvas.crop((0,j*32,32,j*32+32)),NORMAL)

  # Weapon variants reuse canonical pose conditions and virtual tile identities.
  # Only art selection changes; native animation, facing and visibility stay live.
  pose_root=temp/'poses';(pose_root/'capture').mkdir(parents=True);(pose_root/'art').mkdir();(pose_root/'validation').mkdir()
  for f in (ROOT/'art').glob('*.png'):(pose_root/'art'/f.name).symlink_to(f)
  for f in (ROOT/'capture').glob('*-poses.json'):shutil.copy2(f,pose_root/'capture'/f.name)
  existingadds=set(l for l in lines if l.startswith('<addition>'))
  def accept_add(items):
   for l in items:
    if l not in existingadds:existingadds.add(l);adds.append(l)
  condition_defs={l.split(',')[0][11:]:l for l in lines if l.startswith('<condition>')}
  def accept_cond(items):
   for l in items:
    name=l.split(',')[0][11:]
    if name in condition_defs:
     assert condition_defs[name]==l,(name,condition_defs[name],l)
    else:condition_defs[name]=l;conds.append(l)
  for weaponname in ['wide','rocket']:
   for actor,rows,pal in [('spencer',4,0xFF36060F),('overhead-green',2,0xFF202A0F)]:
    records=json.loads((ROOT/f'capture/{actor}-poses.json').read_text())
    for rec in records:
     if actor=='spencer' and 'asset' in rec:continue
     rec['asset']=f'{"spencer"if actor=="spencer"else"overhead"}-{weaponname}-v0100.png';rec['alpha_cutoff']=96
    (pose_root/f'capture/{actor}-poses.json').write_text(json.dumps(records))
    start=len(rules);guard=NORMAL+'&'+('!interception'if actor=='spencer'else'interception')+'&weapon'+weaponname.title()
    c,a,v=make_actor(pose_root,keys,lambda k,p,im,g=None:emit(k,p,im,guard+('&'+g if g else'')),blank,actor,rows,pal)
    namespace='v0100_'+weaponname+'_'+actor.replace('-','_')+'_'
    rename={l.split(',')[0][11:]:namespace+l.split(',')[0][11:] for l in c}
    def renamed(line):
     return re.sub(r'[A-Za-z_][A-Za-z0-9_-]*',lambda m:rename.get(m.group(),m.group()),line)
    c=[renamed(l)for l in c]
    rules[start:]=[renamed(l)for l in rules[start:]]
    accept_cond(c);accept_add(a)
    # Direct overhead parts need the same complete mappings during damage.
    if actor=='overhead-green':
     names={l.split(',')[0][11:] for l in c}
     for line in c:
      name=line.split(',')[0][11:];new=line.replace('<condition>'+name+',','<condition>'+name+'Hit,').replace(',FF202A0F,N',',FF302A0F,N');accept_cond([new])
     for line in rules[start:].copy():
      g,a=parse(line)
      if int(a[2],16)!=pal:continue
      for name in sorted(names,key=len,reverse=True):g=re.sub(r'\b'+name+r'\b',name+'Hit',g)
      a[2]='FF302A0F';rules.append(g+'<tile>'+','.join(a))
  # Hair uses separate native overlay sprites. Its hit palette must be hidden
  # just like the normal red-hair overlay, while the HD body supplies the head.
  for k,p in sorted(observed):
   if p!=0xFF302A0F:continue
   if any(l.startswith('[interception&') and not crop(parse(l)[1]).getchannel('A').getbbox()for l in by[k,0xFF36060F]):
    emit(k,p,blank,'interception&'+NORMAL)
  # All damage palettes retain the original HD body; clone additions AND tiles.
  alias_count=0
  def alias(k,p,source,scope):
   nonlocal alias_count
   if (k,source)not in by:return
   for a in addby[k,source]:
    aa=a.copy();aa[1]=aa[5]=f'{p:08X}';accept_add(['<addition>'+','.join(aa)])
    alias(a[4],p,source,scope)
   for l in by[k,source]:
    g,a=parse(l);im=crop(a);ar=np.array(im)
    if p in {0xFF201515,0xFF202015,0xFF302A0F}:ar[:,:,:3]=np.clip(ar[:,:,:3].astype(float)*[1.10,.82,.72],0,255).astype('uint8')
    gg=g[1:-1]if g else''
    if scope.startswith('area16'):gg=re.sub(r'\barea1[35]\b','area16',gg)
    emit(k,p,Image.fromarray(ar),scope+('&'+gg if gg else''));alias_count+=1
  for k,p in sorted(observed):
   if p in {0xFF201515,0xFF202015} and (k,p)not in by:
    alias(k,p,0xFF36060F if p==0xFF201515 else 0xFF202A0F,NORMAL)
  # Reuse town art and live portrait/terrain rules for the new neutral area.
  area_clones=[]
  for l in lines:
   if not l.startswith('['):continue
   g=l.split(']',1)[0]
   if re.search(r'(?<!!)\barea13\b',g):area_clones.append(re.sub(r'\barea13\b','area16',g)+']'+l.split(']',1)[1])
   elif re.search(r'(?<!!)\barea15\b',g) and 'townRoom'in g:area_clones.append(re.sub(r'\barea15\b','area16',g)+']'+l.split(']',1)[1])
  rules+= [l for l in area_clones if '<tile>'in l];bgs +=[l for l in area_clones if '<background>'in l]
  # New captured palette variants of known painted pickups, barrier and guards.
  for k,p in sorted(observed):
   if p>>24!=255:continue
   src=None
   if k=='0000020E16183800000121110907077F':src=0xFF202A0F
   elif p==0xFF30150F:
    src=0xFF30270F if (k,0xFF30270F)in by else 0xFF36150F
   if src is not None and src!=p:alias(k,p,src,'area16&'+NORMAL)
  # Brief encounter hit puffs share the painted Area 5 burst tiles. They
  # occur under additional overhead palettes, including Spencer's hit flash.
  puff_keys={'0000000000010503080405178F6E1A0C','03050100000000001C6A8E1707050408'}
  for k in sorted(puff_keys):
   candidates=[l for p in sorted(keypal[k])for l in by[k,p]if l.startswith('[area5&')]
   assert candidates,k
   im=crop(parse(candidates[0])[1])
   for p in sorted(keypal[k]):
    if p>>24==255:emit(k,p,im,'interception&'+NORMAL)
  # Door transitions briefly apply the dialogue palette to architectural
  # cells. Cover only observed missing pairs and keep this local to Area 16.
  transition_count=0
  for k,p in sorted(observed):
   if p!=0x0F201C0C or (k,p)in by:continue
   candidates=[l for pp in sorted(keypal[k])for l in by[k,pp]]
   if not candidates:continue
   preferred=[l for l in candidates if l.startswith('[area13&')]
   fallback=[l for l in candidates if l.startswith('<tile>')]
   if not(preferred or fallback):continue
   im=crop(parse((preferred or fallback)[0])[1]);emit(k,p,im,'area16&'+NORMAL);transition_count+=1
  # Upright wheeled turret has three wheel/recoil states in this recording.
  turret_head='090E060606060606070E020202020202';records=[]
  for i,n in enumerate([3175,3988,4310]):
   es=entries('16',n);head=next(e for e in es if e[3]==turret_head);_,ax,ay,_,p,h,v=head;hs=-1 if h else 1
   parts=[[ (x-ax)*hs,y-ay,k,fh^h,fv] for ly,x,y,k,pp,fh,fv in es if ly==1 and pp==p and ax-10<=x<=ax+10 and ay<=y<=ay+24 and k!=turret_head]
   records.append({'id':i,'cell':0,'count':3-i,'head':turret_head,'parts':parts,'frames':[n],'asset':'area16-turret-v0100.png','columns':1,'rows':1,'alpha_cutoff':96})
  (pose_root/'capture/turret-poses.json').write_text(json.dumps(records))
  c,a,v=make_actor(pose_root,keys,lambda k,p,im,g=None:emit(k,p,im,'area16&'+NORMAL+('&'+g if g else'')),blank,'turret',1,0xFF36150F)
  accept_cond(c);accept_add(a)
  # The stationary room contact shares a runner's head but has a new pair
  # of standing legs. Map the full observed pose and suppress its native cells.
  shutil.copy2(ROOT/'capture/v0100/area16-neutral-poses.json',pose_root/'capture/neutral-poses.json')
  start=len(rules)
  c,a,v=make_actor(pose_root,keys,lambda k,p,im,g=None:emit(k,p,im,'area16&'+NORMAL+('&'+g if g else'')),blank,'neutral',1,0xFF30150F)
  rename={l.split(',')[0][11:]:'v0100_'+l.split(',')[0][11:]for l in c}
  def rename_neutral(line):return re.sub(r'[A-Za-z_][A-Za-z0-9_-]*',lambda m:rename.get(m.group(),m.group()),line)
  accept_cond([rename_neutral(l)for l in c]);accept_add(a)
  rules[start:]=[rename_neutral(l)for l in rules[start:]]
  head='3E7F7F7FFF7F7E1D3E7F0F6B4309771F'
  old_virtual={a[4]for (k,p),arrays in addby.items()if k==head for a in arrays}
  for k in sorted(old_virtual):
   for p in sorted(keypal[head]):emit(k,p,blank,'area16&'+NORMAL)
  complete_contact=rules[start:];del rules[start:];rules[0:0]=complete_contact
  # New text character is B in the live dialogue, drawn with the same UI font.
  k='1C22223C22326C000000000000000000';im=Image.new('RGBA',(32,32));ImageDraw.Draw(im).text((16,16),'B',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',34),anchor='mm',fill=(240,236,215))
  emit(k,0x0F201C0C,im,'area16&'+NORMAL)
  # Every new virtual cell is transparent outside its specifically guarded state.
  for l in adds:
   a=l[10:].split(',');emit(a[4],int(a[5],16),blank)
  # There are two overhead encounter IDs. Keep both out of side-view actor rules.
  # Clone positive guards in place; compound negative guards exclude both IDs.
  def encounters(items):
   out=[]
   for l in items:
    if not l.startswith('['):out.append(l);continue
    g,rest=l.split(']',1)
    if '!interception' in g:g=g.replace('!interception','!interception&!interception14')
    out.append(g+']'+rest)
    if re.search(r'(?<!!)\binterception\b',g):out.append(re.sub(r'\binterception\b','interception14',g)+']'+rest)
   return out
  rules=encounters(rules);bgs=encounters(bgs);lines=encounters(lines)
  # Put new rules before the baseline, preserving relative ordering within it.
  lines[0]='# Bionic Commando HD v0.10.0 - Weapons, damage states, and Area 16'
  insert=next(i for i,l in enumerate(lines)if '<tile>'in l)
  prefix=[f'<img>weapons-area16-v0100.png']+conds+adds+bgs+rules
  lines[insert:insert]=list(dict.fromkeys(prefix))
  atlas.crop((0,0,2048,((len(cells)+63)//64)*32)).save(dest/'weapons-area16-v0100.png')
  (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
  readme=(base/'README.txt').read_text().replace('v0.9.8','v0.10.0')
  readme=readme.replace('Area 5 fixed rear nozzle and complete animated exhaust',
   'Distinct equipped weapons, circular rocket shot, damage fixes and Area 16')
  readme=readme.replace('The pistol is the starter design; machine-gun/bazooka player art is still pending.\nEquipment-dependent graphics are supported by the HD engine, not implemented\nfor every weapon in this test build.',
   'The starter gun, three-barrel wide cannon and rocket launcher have distinct held art.\nWeapons beyond the supplied recordings still need review.')
  readme+='\nV0.10.0: Distinct equipped rocket launcher and three-barrel wide cannon; new weapon menu icons; circular rocket projectile; overhead damage and grenade repairs; Area 16 scenery, portraits, turret, barrier, pickup and palette coverage.\n'
  (dest/'README.txt').write_text(readme)
  stats={'version':'0.10.0','new_atlas_cells':len(cells),'new_rules':len(rules),'new_conditions':len(conds),'new_additions':len(adds),'town_rules_extended':len(area_clones),'damage_alias_rules':alias_count,'observed_key_palette_pairs':len(observed),'transition_palette_tiles':transition_count,'weapon_state_address':'04CA','wide_value':2,'rocket_value':1,'overhead_rocket_orb_size':[32,32],'side_view_rocket_orb_size':[64,64]}
  build_stats={'version':'0.10.0','baseline_version':'0.9.8','scale':4,'output_size':[1024,896],'runtime_files':len(list(dest.iterdir())),'tile_rules':sum('<tile>'in l for l in lines),'virtual_sprite_keys':len({tuple(l[10:].split(',')[4:6])for l in lines if l.startswith('<addition>')})}
  (ROOT/'build_stats.json').write_text(json.dumps(build_stats,indent=2)+'\n')
  (ROOT/'validation/v0100-build.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
