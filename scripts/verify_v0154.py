"""Verify the installed Area 8 pack against the full movie and native actor trace."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

from verify_v0110 import structure


def verify(root, native, previous, pack, archive, door_examples):
    starts=(0,10320,16770)
    total=24505
    observations=[]
    for first,last in zip(starts,(*starts[1:],total)):
        run=root/f'run-{first}'
        assert int((run/'home/done').read_text())==last-first
        log=(run/'log').read_text()
        assert not any(s in log for s in ('Condition not found','[HDPack - Line','Script error'))
        for filename,width in [('ram.bin',2048),('oam.bin',256),('palette.bin',32)]:
            with (native/filename).open('rb') as stream:
                stream.seek(first*width)
                assert stream.read((last-first)*width)==(run/filename).read_bytes()
        observations.append(np.loadtxt(run/'flight.tsv',dtype=int,ndmin=2))
    rows=np.concatenate(observations)
    memory=np.memmap(native/'ram.bin',mode='r',dtype='u1',shape=(total,2048))
    expected=set()
    for slot in (8,9,10):
        pose=memory[:,0x5e4+slot]
        active=(memory[:,0x536+slot]==1)&(memory[:,0x55c+slot]==0)&(memory[:,0x596+slot]==0)
        active&=(memory[:,0x4d]==8)&(memory[:,0xff]==0x1a)&np.isin(pose,[0x92,0xb0])
        expected.update((int(n)+1,slot) for n in np.flatnonzero(active))
    assert len(expected)==len(rows)
    assert expected=={(int(n),int(slot)) for n,slot in rows[:,:2]}
    assert np.all(rows[:,6]>0) and np.all(rows[:,7]>0)
    def image(n):
        start=max(t for t in starts if t<n)
        data=(root/f'run-{start}'/f'{n}.bgra').read_bytes()
        return np.asarray(Image.frombytes('RGB',(1024,896),data,'raw','BGRX'))
    tests=json.loads(door_examples.read_text())['examples']
    tests=[q for q in tests if q['frame']!=13728]
    tests.append(dict(kind='radio',frame=17496,x=96,y=30))
    controls=[]
    for q in tests:
        n=q['frame'];x=4*q['x'];y=4*(q['y']-8)
        new=image(n);old=np.asarray(Image.open(previous/'frames'/f'{n:05}.png').convert('RGB'))
        if q['kind']!='goal':
            assert np.array_equal(new[y:y+128,x:x+128],old[y:y+128,x:x+128]);controls.append(n)
            continue
        plaque=np.asarray(Image.open(pack/'boss-door-eagle-v0115.png').convert('RGB')).astype(int)
        crop=new[y:y+32,x+32:x+96]
        assert np.abs(crop.astype(int)-plaque).mean()<2
        changed=np.any(old!=new,axis=2);changed[y:y+32,x+32:x+96]=False;assert not changed.any()
    # Spencer occludes part of the sign while entering the final door.
    entering=image(22512);earlier=np.asarray(Image.open(previous/'frames/22512.png').convert('RGB'))
    changed=np.any(entering!=earlier,axis=2);box=changed[476:508,864:928].copy()
    changed[476:508,864:928]=False
    assert 0<box.sum()<box.size and not changed.any()
    with ZipFile(archive)as z:
        assert z.testzip() is None
        assert {Path(n).name for n in z.namelist()}=={f.name for f in pack.iterdir()}
        for name in z.namelist():assert z.read(name)==(pack/Path(name).name).read_bytes()
    sizes={f.name:(1152,1104) for f in pack.glob('area8-recoil-*-v0152.png')}
    sizes.update({f.name:(1200,1220) for f in pack.glob('area8-chute-*-v0154.png')})
    _,perframe=np.unique(rows[:,0],return_counts=True)
    return dict(recording_frames=total,synchronized_replay_segments=3,
                frames_with_airborne_soldiers=len(perframe), simultaneous_drop_frames=int((perframe>1).sum()),
                airborne_soldier_frames=len(rows),red_soldier_frames=int((rows[:,2]==0x92).sum()),
                blue_soldier_frames=int((rows[:,2]==0xb0).sum()),frames_without_visible_soldier_art=int((rows[:,7]==0).sum()),
                unchanged_passage_and_radio_door_controls=controls,eagle_approach=22368,eagle_entry=22512,
                archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),structure=structure(pack,sizes))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['captures','native','previous','pack','archive','door_examples']:parser.add_argument(name,type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(*vars(args).values()),indent=2))
