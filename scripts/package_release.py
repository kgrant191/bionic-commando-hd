"""Build the Mesen installer from its checked-in artwork and rules."""
import argparse
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="destination ZIP file")
    output = parser.parse_args().output
    pack = Path(__file__).resolve().parents[1] / "pack"
    files = sorted(pack.iterdir(), key=lambda path: path.name)
    if not all(path.is_file() for path in files):
        raise ValueError("The installer expects a flat pack directory.")
    rules = pack.parent / "pack-source"
    sources = {path.name: [path] for path in files}
    sources["hires.txt"] = [rules / "hires.part1.txt", rules / "hires.part2.txt"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as staging:
        temporary = Path(staging) / output.name
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
            for name, paths in sorted(sources.items()):
                entry = ZipInfo(name, date_time=(2026, 11, 23, 0, 0, 0))
                entry.compress_type = ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                with archive.open(entry, "w") as target:
                    for path in paths:
                        with path.open("rb") as source:
                            copyfileobj(source, target)
        temporary.replace(output)


if __name__ == "__main__":
    main()
