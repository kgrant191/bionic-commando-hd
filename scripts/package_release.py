"""Build the v1.0.0 Mesen installer from the checked-in pack directory."""
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
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as staging:
        temporary = Path(staging) / output.name
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
            for path in files:
                entry = ZipInfo(path.name, date_time=(2026, 11, 23, 0, 0, 0))
                entry.compress_type = ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                with path.open("rb") as source, archive.open(entry, "w") as target:
                    copyfileobj(source, target)
        temporary.replace(output)


if __name__ == "__main__":
    main()
