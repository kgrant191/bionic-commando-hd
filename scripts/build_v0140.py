"""Build Area 14 on top of the approved v0.13.3 installable pack."""
import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ATLAS = "area14-town-items-v0140.png"
STAGE = "area14&!worldmap&!equipment&!title&!radio&!areaClear"
OLD_HEAD = "FDDE2E1EFE1E0D0D7130104000E0F0F0"
PIT = {
    "0081C1737F3812320000804044271D0D", "F0F0381F3F3B71C10FDF3F0704083040",
    "0002069CFC3810180000020444C8F0E0", "1E1E38F0F8B81C06E0E6F8C040201804",
}


def inventory_icons():
    src = Image.open(ROOT / "art/area14-inventory-v0140.png").convert("RGBA")
    w, h = src.width // 2, src.height // 2
    icons = {}
    for i, name in enumerate(("medicine", "pendant", "permit", "rapid_fire")):
        x, y = (i % 2) * w, (i // 2) * h
        icon = src.crop((x, y, x + w, y + h))
        box = icon.getchannel("A").point(lambda a: 255 if a > 64 else 0).getbbox()
        icon = icon.crop(box)
        icon.thumbnail((60, 60), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (64, 64))
        canvas.alpha_composite(icon, ((64 - icon.width) // 2, (64 - icon.height) // 2))
        icons[name] = canvas
    return icons


def expressions():
    src = Image.open(ROOT / "art/area14-green-contact-v0140.png").convert("RGBA")
    w, h = src.size
    closed, speaking = [
        src.crop((i * w // 2, 0, (i + 1) * w // 2, h)).resize((192, 256), Image.Resampling.LANCZOS)
        for i in range(2)
    ]
    # Register the nose and eyes, then take only the lower face from the talking
    # painting. Hair, jacket and shoulders consequently stay still between poses.
    aligned = Image.new("RGBA", closed.size)
    aligned.paste(speaking, (2, 0))
    mask = Image.new("L", closed.size)
    ImageDraw.Draw(mask).ellipse((52, 83, 105, 121), fill=255)
    mouth = Image.composite(aligned, closed, mask.filter(ImageFilter.GaussianBlur(1.7)))
    return closed, mouth


def gamma_tile():
    # The ROM's Greek communicator designation is a live glyph within the dialogue line.
    tile = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
    font = ImageFont.truetype("DejaVuSans-BoldOblique.ttf", 32)
    ImageDraw.Draw(tile).text((16, 16), "γ", font=font, fill=(255, 254, 255), anchor="mm")
    return tile


def build(source, target):
    source, target = source.resolve(), target.resolve()
    assert source != target
    target.mkdir(parents=True, exist_ok=True)
    for file in source.iterdir():
        if file.is_file():
            shutil.copy2(file, target / file.name)
    lines = (source / "hires.txt").read_text().splitlines()
    assert "v0.13.3" in lines[0]
    sheets = [r[5:] for r in lines if r.startswith("<img>")]
    img_id = len(sheets)
    priors, cells, locs = [], [], {}
    def emit(key, palette, image, guard):
        content = image.tobytes()
        if content not in locs:
            locs[content] = len(cells)
            cells.append(image)
        i = locs[content]
        priors.append(f"[{guard}]<tile>{img_id},{key},{palette},{(i % 32) * 32},{(i // 32) * 32},1,N")

    record = json.loads((ROOT / "capture/area14/inventory.json").read_text())
    for name, icon in inventory_icons().items():
        for x, y, key, pal in record[name]:
            tx, ty = 4 * x, 4 * y
            emit(key, pal, icon.crop((tx, ty, tx + 32, ty + 32)), "equipment")

    frames = expressions()
    positions = {}
    for line in lines:
        if line.startswith("<addition>" + OLD_HEAD + ",FF263506,"):
            _, _, x, y, virtual, _, _ = line[10:].split(",")
            positions[virtual] = ((int(x) + 32) * 4, (int(y) + 24) * 4)
    assert len(positions) == 48
    face_rows = 0
    for line in lines:
        if not line.startswith("[area13&") or "<tile>" not in line:
            continue
        guard, fields = line.split("<tile>")
        _, key, palette, *_ = fields.split(",")
        if key not in positions:
            continue
        x, y = positions[key]
        mouth = re.search(r"&a13mouth\d+", guard)
        flag = STAGE + "&a14ContactLo&a14ContactHi" + (mouth.group() if mouth else "")
        emit(key, palette, frames[bool(mouth)].crop((x, y, x + 32, y + 32)), flag)
        face_rows += 1
    assert face_rows == 96

    emit("2C123050505020000000000000000000", "0F201C0C", gamma_tile(), STAGE)
    pit_sheet = sheets.index("area6-hazards-v0132.png")
    hazard = []
    for r in lines:
        if "<tile>" not in r:
            continue
        f = r.split("<tile>")[1].split(",")
        if int(f[0]) == pit_sheet and f[1] in PIT and f[2] == "FF30210F":
            f[2] = "FF36150F"
            hazard.append("[" + STAGE + "]<tile>" + ",".join(f))
    assert len(hazard) == 4

    # Areas 13 and 15 shared this pack's town art. Include only Area 14 in
    # that same dispatch, preserving per-area overrides and renderer priority.
    region = re.compile(r"(?<=[\[&])area13(?=[&\]])")
    for i, row in enumerate(lines):
        if row.startswith("["):
            lines[i] = region.sub("townFrom13&townTo15", row)
    pos = next(i for i, r in enumerate(lines) if r.startswith("<condition>area13,"))
    lines[pos:pos] = [
        "<condition>townFrom13,memoryCheckConstant,004D,>=,0D",
        "<condition>townTo15,memoryCheckConstant,004D,<=,0F",
        "<condition>area14,memoryCheckConstant,004D,==,0E",
        # The dialogue script address is selected before the first face tile.
        "<condition>a14ContactLo,memoryCheckConstant,007A,==,4C",
        "<condition>a14ContactHi,memoryCheckConstant,007B,==,92",
    ]
    sheet = Image.new("RGBA", (1024, ((len(cells) + 31) // 32) * 32))
    for i, cell in enumerate(cells):
        sheet.paste(cell, (i % 32 * 32, i // 32 * 32))
    sheet.save(target / ATLAS, optimize=True)
    first = next(i for i, r in enumerate(lines) if "<tile>" in r)
    lines[first:first] = ["<img>" + ATLAS] + priors + hazard
    lines[0] = "# Bionic Commando HD v0.14.0 - Area 14 neutral town and equipment"
    (target / "hires.txt").write_text("\n".join(lines) + "\n")
    readme = (source / "README.txt").read_text().replace("v0.13.3", "v0.14.0", 1)
    readme = readme.replace("Area 6 review build", "Area 14 review build", 1)
    readme = readme.replace("NEW IN THIS BUILD\n", "NEW IN THIS BUILD\nArea 14 neutral town, speaker-matched portraits and the gamma communicator text.\nNew equipment artwork for medicine, pendant, permit and rapid-fire device.\n\nPREVIOUS BUILDS\n", 1)
    (target / "README.txt").write_text(readme)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    build(args.source, args.target)
