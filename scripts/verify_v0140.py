"""Check the replay of 14.mmo against its original ROM and the approved v0.13.3 pack."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

from build_v0140 import ROOT, inventory_icons
from verify_v0110 import structure


def run(root, archive):
    original, before, final = [root / folder for folder in ("original", "before", "final")]
    assert (final / "home/done").read_text() == "4385"
    for name, size in (("ram.bin", 2048), ("palette.bin", 32), ("oam.bin", 256)):
        raw = (original / name).read_bytes()
        assert len(raw) == size * 4385
        assert raw == (before / name).read_bytes() == (final / name).read_bytes()
    portraits = defaultdict(Counter)
    first_last = defaultdict(list)
    for r in (final / "portraits.tsv").read_text().splitlines():
        frame, actor, talking, x, y, fingerprint, green, white, visible = map(int, r.split())
        if actor == 1:
            assert white > 15000 and green < 200
        else:
            assert actor == 2 and green > 12000 and white < 1500
        assert visible > 25000
        portraits[actor, talking][fingerprint] += 1
        first_last[actor].append(frame)
    assert set(portraits) == {(1, 0), (1, 1), (2, 0), (2, 1)}
    assert all(len(states) == 1 for states in portraits.values())
    assert len({next(iter(states)) for states in portraits.values()}) == 4
    assert all(frames == list(range(frames[0], frames[-1] + 1)) for frames in first_last.values())

    record = json.loads((ROOT / "capture/area14/inventory.json").read_text())
    icons = inventory_icons()
    quadrants = {}
    for name, rows in record.items():
        for dx, dy, key, pal in rows:
            quadrants[key, pal] = (name, np.asarray(icons[name].crop((dx*4, dy*4, dx*4+32, dy*4+32))))
    uses = defaultdict(set)
    menu_frames = 0
    map_frames = 0
    for p in sorted((final / "frames").glob("*.png")):
        n = int(p.stem)
        if n <= 648 or n >= 4176:
            assert p.read_bytes() == (before / "frames" / p.name).read_bytes()
            map_frames += 1
        if not 744 <= n <= 1104:
            continue
        rgb = np.array(Image.open(p).convert("RGB"))
        old = np.array(Image.open(before / "frames" / p.name).convert("RGB"))
        delta = np.any(rgb != old, axis=2)
        for row in p.with_suffix(".tiles").read_text().splitlines():
            layer, x, y, key, pal, h, v = row.split(",")
            if layer != "1" or (key, pal) not in quadrants:
                continue
            name, quad = quadrants[key, pal]
            x, y = int(x)*4, (int(y)-8)*4
            assert (h,v) == ("0","0")
            region = rgb[y:y+32, x:x+32]
            solid = quad[:,:,3] == 255
            if solid.any():
                assert np.array_equal(region[solid], quad[:,:,:3][solid]), (n,name,x,y)
            delta[y:y+32,x:x+32] = False
            uses[name].add("equipped" if y >= 700 else "selection")
        assert not delta.any(), ("unexpected inventory change", n)
        menu_frames += 1
    assert set(uses) == set(record)
    for name in ("medicine", "pendant", "permit"):
        assert uses[name] == {"selection", "equipped"}
    pack = root / "installed"
    with ZipFile(archive) as z:
        assert not z.testzip()
        assert set(z.namelist()) == {p.name for p in pack.iterdir()}
        assert all(z.read(p.name) == p.read_bytes() for p in pack.iterdir())
    assert not any(word in (final / "log").read_text().lower() for word in ("invalid condition","unable to load", "script error","exception"))
    return dict(movie_frames=4385, identical_ram_oam_and_palette_frames=4385,
                identical_world_map_samples=map_frames, equipment_samples=menu_frames,
                equipment_views={name:sorted(locations) for name,locations in uses.items()},
                portrait_frames={name: {"closed": sum(portraits[i,0].values()), "speaking":sum(portraits[i,1].values())}
                                 for i,name in [(1,"white_guard"),(2,"green_contact")]},
                runtime=structure(pack),zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())


if __name__ == "__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("replay_directory",type=Path)
    cli.add_argument("archive",type=Path)
    args=cli.parse_args()
    print(json.dumps(run(args.replay_directory,args.archive),indent=2))
