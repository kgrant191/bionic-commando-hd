"""Structural checks, replay equivalence, and the observed direction audit."""
from pathlib import Path
import argparse,hashlib,json,re
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--replay-root',type=Path,default=ROOT.parent/'replay');args=ap.parse_args()
    pack=ROOT/'pack';lines=(pack/'hires.txt').read_text().splitlines()
    images=[];names=set();known=set();fallbacks=set();adds=[]
    for l in lines:
        if l.startswith('<img>'):images.append(Image.open(pack/l[5:]))
        if l.startswith('<condition>'):
            n=l[11:].split(',')[0];assert n not in names,n;names.add(n)
        if l.startswith('['):
            assert all(not n or n in names for n in re.split('[&|!()]',l[1:].split(']')[0])),l
        if '<tile>'in l:
            a=l.split('<tile>')[1].split(',');i,x,y=int(a[0]),int(a[3]),int(a[4])
            assert 0<=i<len(images) and x>=0 and y>=0 and x+32<=images[i].width and y+32<=images[i].height,l
            known.add(tuple(a[1:3]))
            if l.startswith('<tile>'):fallbacks.add(tuple(a[1:3]))
        if l.startswith('<addition>'):adds.append(tuple(l[10:].split(',')))
    assert len({a[:4]+a[6:]for a in adds})==len(adds),'Repeated addition anchor'
    assert all(tuple(a[:2])in known and tuple(a[4:6])in fallbacks for a in adds)
    results={}
    for movie,frames,step,before in [('issue1-enemy',2010,30,'original'),('16',7792,30,'original'),('directions-test',420,1,'original'),('regression-boss',1940,30,'before')]:
        mode='v0101-final' if movie in {'issue1-enemy','directions-test'} else 'v0101'
        d=args.replay_root/movie/mode;src=args.replay_root/movie/before
        assert (d/'home/done').exists(),movie
        for n in sorted({1,frames}|set(range(step,frames+1,step))):
            for ext in ['ram','ppu']:
                f=f'{n:05d}.{ext}';assert(d/'frames'/f).read_bytes()==(src/'frames'/f).read_bytes(),(movie,f)
        installed=d/'home/HdPacks/Bionic Commando (USA)'
        different=[p.name for p in pack.iterdir()if p.name!='README.txt'and p.read_bytes()!=(installed/p.name).read_bytes()]
        equivalence='exact final runtime'
        if different:
            # The last edit only narrows overhead native-piece suppression.
            # Prove that every image, addition, and non-overhead rule in the
            # town/boss replay is identical to the final installable runtime.
            assert movie in {'16','regression-boss'} and different==['hires.txt'],(movie,different)
            def unaffected(path):
                return [l for l in path.read_text().splitlines() if not l.startswith('<condition>v0101Near') and not(l.startswith('[')and re.search(r'(?<!!)\binterception(?:14)?\b',l.split(']')[0]))]
            assert unaffected(pack/'hires.txt')==unaffected(installed/'hires.txt')
            # No sampled game state in these recordings enters an encounter.
            assert all((d/'frames'/f'{n:05}.ram').read_bytes()[0x4c]not in {0x13,0x14} for n in sorted({1,frames}|set(range(step,frames+1,step))))
            equivalence='same images/additions and identical non-overhead rules; last overhead-only edit inactive in this replay'
        log=(d/'log.txt').read_text();assert 'HD enabled: 1'in log
        assert not re.search(r'\[HDPack\].*(?:error|invalid|unable)|script error|Exception',log,re.I)
        shots=[p for p in(d/'frames').glob('*.png')if p.stat().st_size>100]
        assert all(Image.open(p).size==(1024,896)for p in shots)
        if movie=='regression-boss':
            for p in shots:
                assert np.array_equal(np.array(Image.open(p)),np.array(Image.open(src/'frames'/p.name))),p.name
        results[movie]={'movie_frames':frames,'matching_RAM_PPU_checkpoints':len({1,frames}|set(range(step,frames+1,step))),'screenshots':len(shots),'runtime_evidence':equivalence}
    # The direction diagnostic changes only a copy of the movie's input track.
    # Confirm the actual player anchor for all eight requested directions.
    expected=['161108','302D17','6F88F8','0C38F0','58381B','0C38F0','6F88F8','302D17']
    direction_results=[]
    for n,prefix in zip(range(310,421,15),expected):
        p=args.replay_root/f'directions-test/original/tiles/{n:05d}.tiles'
        es=[l.split(',')for l in p.read_text().splitlines()]
        found=[a for a in es if a[0]=='1'and a[3].startswith(prefix)and int(a[2])>80 and int(a[4])==0xFF202A0F]
        assert len(found)==1,(n,found)
        direction_results.append({'frame':n,'anchor':found[0][3],'flip_x':int(found[0][5])})
    report={'version':'0.10.1','recordings':results,'eight_direction_test':direction_results,'duplicate_addition_anchors':0,
            'limits':'All supplied frames replayed; RAM/PPU checked at 30-frame intervals and endpoints. Overhead screenshots captured every frame, Area 16 every three frames. Visual review uses dense motion strips and selected scenes; unrecorded areas remain untested.',
            'pack_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(pack.iterdir())}}
    (ROOT/'validation/v0101-replay.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='pack_sha256'},indent=2))

if __name__=='__main__':main()
