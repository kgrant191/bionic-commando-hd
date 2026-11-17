"""Load an immutable, hash-verified runtime baseline from a directory or ZIP."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def copy_baseline(source, destination, version):
    source, destination = Path(source), Path(destination)
    manifest = json.loads((ROOT / 'baselines' / f'v{version}.json').read_text())
    if source.is_dir():
        actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in source.iterdir() if p.is_file()}
        assert actual == manifest['files'], f'Unexpected v{version} baseline contents'
        destination.mkdir(parents=True, exist_ok=True)
        for name in manifest['files']:
            shutil.copy2(source / name, destination / name)
    else:
        assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['zip_sha256']
        with zipfile.ZipFile(source) as archive:
            assert set(archive.namelist()) == set(manifest['files'])
            archive.extractall(destination)
    return manifest['zip_sha256']
