"""Use the complete painted field character for every Area 14 movement phase."""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = "area14&!worldmap&!equipment&!title&!radio&!areaClear"
BLANK = (6, 96, 0)


def build(source, target):
    source, target = source.resolve(), target.resolve()
    assert source != target
    target.mkdir(parents=True, exist_ok=True)
    for file in source.iterdir():
        if file.is_file():
            shutil.copy2(file, target / file.name)
    lines = (source / "hires.txt").read_text().splitlines()
    assert "v0.14.0" in lines[0]
    records = json.loads((ROOT / "capture/area14/field-poses-v0141.json").read_text())
    additions = [r[10:].split(",") for r in lines if r.startswith("<addition>")]
    definitions, rules = {}, []

    def nearby(dx, dy, key, palette):
        token = (dx, dy, key, palette)
        if token not in definitions:
            definitions[token] = f"town141Near{len(definitions)}"
        # The game never flips these actors vertically. Bound the neighbor lookup
        # when a moving platform or a door transition puts a sprite at the screen edge.
        bounds = ""
        if dy:
            boundary = (">=", -dy) if dy < 0 else ("<", 240 - dy)
            if boundary not in definitions:
                definitions[boundary] = f"town141Y{len(definitions)}"
            bounds = "&" + definitions[boundary]
        return bounds + "&" + definitions[token]

    def emit(key, pal, tile, suffix=""):
        idx, x, y = tile
        rules.append(f"[{STAGE}{suffix}]<tile>{idx},{key},{pal},{x},{y},1,N")

    for name, actor in records.items():
        head, pal, poses = actor["head"], actor["palette"], actor["poses"]
        overlays = {(int(x), int(y)): key for src, p, x, y, key, _, _ in additions if src == head and p == pal}
        painted = {label: {(x,y): (i,tx,ty) for x,y,i,tx,ty in pose["cells"]} for label,pose in poses.items()}
        assert overlays and all(set(cells) <= set(overlays) for cells in painted.values())
        fallback = "rest" if name == "green" else "compact"
        markers = {}
        for label, pose in poses.items():
            others = {part[2] for other, table in poses.items() if other != label for part in table["parts"]}
            # An overlapping actor may obscure only part of a native tile. Either shin
            # or thigh identifies the same phase even when its opposite leg is hidden.
            locations = [tuple(pose["signature"])]
            for dx,dy,key,_,_ in pose["parts"]:
                if dy >= 15 and key not in others and int(key,16).bit_count() >= 8:
                    locations.append((dx,dy,key))
            markers[label] = list(dict.fromkeys(locations))
        for (x,y), virtual in overlays.items():
            # The stationary contact and Spencer share a walking palette, so his
            # own standing legs take precedence when Spencer passes in front.
            order = (["rest"] if name == "green" else []) + [p for p in poses if p != fallback]
            for label in order:
                for sx,sy,native in markers[label]:
                    emit(virtual, pal, painted[label].get((x,y),BLANK), nearby(sx-x,sy-y,native,pal))
            emit(virtual, pal, painted[fallback].get((x,y),BLANK))
        # The head contributes the HD overlay. Remove its original pixels and
        # only the native limbs in their offsets for that actor. Spencer can
        # share a pattern or palette with a town NPC while standing beside him.
        emit(head, pal, BLANK)
        parts = {tuple(p) for pose in poses.values() for p in pose["parts"]}
        # Two consistent upper-body landmarks also cover clipping or overlap of
        # the head tile. Match both the palette and the original relative position.
        alt_pos = (0,8) if name == "red" else (8,0)
        alt = next(k for x,y,k,h,v in poses["rest"]["parts"] if (x,y)==alt_pos)
        for x,y,key,h,v in sorted(parts):
            if (x,y) == (0,0) and key == head:
                continue
            for sx,sy,anchor in [(0,0,head),(*alt_pos,alt)]:
                emit(key,pal,BLANK,nearby((sx-x)*(-1 if h else 1),(sy-y)*(-1 if v else 1),anchor,pal))

    conditions = []
    for token,name in definitions.items():
        if len(token) == 2:
            op,cutoff = token
            conditions.append(f"<condition>{name},positionCheckY,{op},{cutoff}")
        else:
            x,y,key,pal = token
            conditions.append(f"<condition>{name},spriteNearby,{x},{y},{key},{pal},N")
    first = next(i for i,r in enumerate(lines) if "<tile>" in r)
    lines[first:first] = conditions + list(dict.fromkeys(rules))
    lines[0] = "# Bionic Commando HD v0.14.1 - Area 14 field character animation"
    (target / "hires.txt").write_text("\n".join(lines) + "\n")
    readme = (source / "README.txt").read_text().replace("v0.14.0","v0.14.1",1)
    readme = readme.replace("NEW IN THIS BUILD\n","NEW IN THIS BUILD\nComplete white and red runner strides and all-green field contact.\n\nPREVIOUS BUILDS\n",1)
    (target / "README.txt").write_text(readme)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("target", type=Path)
    args = p.parse_args()
    build(args.source,args.target)
