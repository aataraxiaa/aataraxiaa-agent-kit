#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'plugins/aataraxiaa/vendor'
REVISION = json.loads((DEST / 'provenance.json').read_text())['revision']


def manifest():
    return {str(p.relative_to(DEST)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(DEST.rglob('*')) if p.is_file() and p.name != 'provenance.json'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', nargs='?')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    provenance = DEST / 'provenance.json'
    if args.check:
        saved = json.loads(provenance.read_text())
        if saved['files'] != manifest():
            raise SystemExit('Vendored files differ from pinned checksums')
        print('Pinned upstream checksums match')
        return
    if not args.checkout:
        parser.error('Supply a local upstream Git checkout, or use --check')
    checkout = Path(args.checkout).resolve()
    def git(*cmd):
        return subprocess.check_output(['git', '-C', str(checkout), *cmd])
    git('cat-file', '-e', REVISION + '^{commit}')
    paths = git('ls-tree', '-r', '--name-only', REVISION, 'plugins/visual-explainer', 'LICENSE').decode().splitlines()
    if (DEST / 'visual-explainer').exists():
        shutil.rmtree(DEST / 'visual-explainer')
    DEST.mkdir(parents=True, exist_ok=True)
    for name in paths:
        if 'node_modules' in Path(name).parts:
            continue
        relative = name.removeprefix('plugins/') if name != 'LICENSE' else 'LICENSE'
        path = DEST / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(git('show', REVISION + ':' + name))
    provenance.write_text(json.dumps(dict(repository='https://github.com/nicobailon/visual-explainer', revision=REVISION,
        version='0.14.0', license='LICENSE', files=manifest()), indent=2) + '\n')
    print('Copied tracked upstream files at ' + REVISION)


if __name__ == '__main__':
    main()
