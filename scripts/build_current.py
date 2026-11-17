"""Rebuild the approved runtime from the preserved v0.9.6 baseline and patches."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'pack')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='bionic-v098-') as scratch:
        intermediate = Path(scratch) / 'v097'
        finished = Path(scratch) / 'v098'
        for version, source, target in [('097', ROOT / 'baselines/v096', intermediate),
                                        ('098', intermediate, finished)]:
            subprocess.run([sys.executable, str(ROOT / 'scripts' / f'apply_v{version}.py'),
                            str(source), str(ROOT / 'capture' / f'v{version}'), str(target)], check=True)
        expected = json.loads((ROOT / 'baselines/v098.json').read_text())['files']
        actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in finished.iterdir()}
        assert actual == expected, 'Rebuild differs from the approved runtime'
        args.output.mkdir(parents=True, exist_ok=True)
        shutil.copytree(finished, args.output, dirs_exist_ok=True)
        stats = {
            'version': '0.9.8', 'baseline_version': '0.9.6',
            'scale': 4, 'output_size': [1024, 896],
            'runtime_files': len(actual),
            'tile_rules': sum('<tile>' in line for line in (finished / 'hires.txt').read_text().splitlines()),
            'approved_runtime_hashes_match': True,
        }
        (ROOT / 'build_stats.json').write_text(json.dumps(stats, indent=2) + '\n')
        print(f'Rebuilt all {len(actual)} approved v0.9.8 runtime files: {args.output}')

if __name__ == '__main__':
    main()
