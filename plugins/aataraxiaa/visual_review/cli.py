import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from .core import Journal, WorkflowError
from .hooks import handle

PLUGIN = Path(__file__).resolve().parents[1]


def present(path):
    opener = ['open'] if sys.platform == 'darwin' else ['cmd', '/c', 'start', ''] if sys.platform == 'win32' else ['xdg-open']
    subprocess.run([*opener, str(path)], check=True, capture_output=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Source-bound interactive visual review receipts')
    parser.add_argument('--cwd', default=os.getcwd())
    parser.add_argument('--session', default=os.environ.get('CLAUDE_SESSION_ID', os.environ.get('CODEX_SESSION_ID')))
    sub = parser.add_subparsers(dest='action', required=True)
    begin = sub.add_parser('begin')
    begin.add_argument('--kind', choices=['implementation','plan','code-review','pr-review','discussion'], required=True)
    begin.add_argument('--scope', required=True)
    begin.add_argument('--base')
    begin.add_argument('--target')
    begin.add_argument('--pending', action='store_true')
    begin.add_argument('--new', action='store_true')
    resolve = sub.add_parser('resolve')
    resolve.add_argument('--base', required=True)
    resolve.add_argument('--target', required=True)
    include = sub.add_parser('include')
    include.add_argument('--path', required=True)
    sub.add_parser('status')
    check = sub.add_parser('check')
    check.add_argument('--publish', action='store_true')
    check.add_argument('--editing', action='store_true')
    for name in ('render', 'record'):
        p = sub.add_parser(name)
        p.add_argument('--stage', choices=['plan','post','review'], required=True)
        p.add_argument('--source' if name == 'render' else '--html', required=True)
        p.add_argument('--present', action='store_true', required=True)
    sub.add_parser('hook')
    args = parser.parse_args(argv)
    try:
        if args.action == 'hook':
            event = json.load(sys.stdin)
            try:
                result = handle(event)
            except (WorkflowError, OSError, subprocess.CalledProcessError) as exc:
                message = 'Visual-review could not certify this workflow: ' + str(exc)
                result = {'systemMessage': message + '. Continuing without enforcement.'}
            print(json.dumps(result))
            return 0
        journal = Journal(args.cwd, args.session)
        if args.action == 'begin':
            task = journal.begin(args.kind, args.scope, args.base, args.target, args.pending, args.new)
        elif args.action == 'include':
            if not journal.load():
                raise WorkflowError('Begin a task before including a worktree')
            task = journal.include_target(args.path)
        elif args.action == 'resolve':
            task = journal.resolve(args.base, args.target)
        elif args.action in ('render', 'record'):
            if args.action == 'render':
                source = journal.artifact(args.source)
                output = source.with_name(source.name.replace('.src.html', '.html'))
                if output == source:
                    raise WorkflowError('Source filename must end in .src.html')
                subprocess.run(['node', str(PLUGIN / 'vendor/visual-explainer/kit/render.mjs'), str(source), '-o', str(output), '--root', str(journal.cwd), '--no-check'], check=True)
            else:
                output = journal.artifact(args.html)
            task = journal.receipt(args.stage, output, present)
        elif args.action == 'check':
            missing = journal.missing(publish=args.publish, editing=args.editing)
            print(json.dumps({'missing': missing}))
            return 1 if missing else 0
        else:
            task = journal.load()
        print(json.dumps({'task': task, 'missing': journal.missing(task), 'artifacts': str(journal.root)}, indent=2))
        return 0
    except (WorkflowError, OSError, subprocess.CalledProcessError) as exc:
        print('visual-review: ' + str(exc), file=sys.stderr)
        return 2
