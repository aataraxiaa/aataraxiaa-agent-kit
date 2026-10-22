import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import uuid


class WorkflowError(Exception):
    pass


def digest(value):
    return hashlib.sha256(value).hexdigest()


def git(cwd, *args, check=True):
    return subprocess.run(['git', '-C', str(cwd), *args], capture_output=True, check=check).stdout


def canonical(cwd):
    cwd = Path(cwd).resolve()
    root = git(cwd, 'rev-parse', '--show-toplevel', check=False).decode().strip()
    return Path(root).resolve() if root else cwd


def artifact_root(cwd):
    helper = Path.home() / '.agents/bin/agent-task-dir'
    if helper.is_file():
        result = subprocess.run([str(helper)], cwd=cwd, capture_output=True, text=True, check=True)
        root = Path(result.stdout.strip()).expanduser().resolve()
    elif os.environ.get('AGENT_ARTIFACTS_DIR'):
        root = Path(os.environ['AGENT_ARTIFACTS_DIR']).expanduser().resolve()
    else:
        key = os.environ.get('AGENT_PROJECT_DIR', str(cwd))
        root = Path.home() / '.agents-work' / ('visual-review-' + digest(key.encode())[:20])
    if root == cwd or cwd in root.parents:
        raise WorkflowError('Artifact directory must be outside the application worktree')
    result = root / 'review-artifacts/visual-review'
    result.mkdir(parents=True, exist_ok=True)
    return result


def fingerprint(cwd, base=None, target=None):
    h = hashlib.sha256()
    def add(value):
        h.update(len(value).to_bytes(8, 'big'))
        h.update(value)
    inside = git(cwd, 'rev-parse', '--is-inside-work-tree', check=False).strip() == b'true'
    if inside:
        add(git(cwd, 'rev-parse', '--verify', 'HEAD', check=False))
        add(git(cwd, 'ls-files', '--stage', '-z'))
        status = git(cwd, 'status', '--porcelain=v1', '-z', '--untracked-files=all', '--ignore-submodules=none')
        add(status)
        dirty_names = [part[3:] if len(part) > 3 and part[2:3] == b' ' else part for part in status.split(b'\0') if part]
        if any('.env' == Path(os.fsdecode(n)).name or Path(os.fsdecode(n)).name.startswith('.env.') for n in dirty_names):
            raise WorkflowError('Dirty or untracked .env files prevent certification; their content is never read')
        names = set(git(cwd, 'diff', '--name-only', '-z', '--no-renames', '--ignore-submodules=none').split(b'\0'))
        names.update(git(cwd, 'ls-files', '-z', '--others', '--exclude-standard').split(b'\0'))
        names.discard(b'')
        for name in sorted(names):
            path = cwd / os.fsdecode(name)
            add(name)
            if path.name == '.env' or path.name.startswith('.env.'):
                add(b'clean secret file: index binding only')
                continue
            if path.is_symlink():
                add(b'link:' + os.fsencode(os.readlink(path)))
            elif path.is_file():
                add(path.read_bytes())
                add(str(path.stat().st_mode).encode())
            elif path.is_dir():
                if canonical(path) == path.resolve():
                    add(json.dumps(fingerprint(path), sort_keys=True).encode())
                else:
                    add(b'uninitialized submodule')
            else:
                add(b'deleted')
    else:
        for path in sorted(cwd.rglob('*')):
            if '.git' in path.parts or not path.is_file():
                continue
            if path.name == '.env' or path.name.startswith('.env.'):
                raise WorkflowError('Non-Git .env files prevent certification; their content is never read')
            add(str(path.relative_to(cwd)).encode())
            add(os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes())
    refs = {}
    for key, ref in [('base', base), ('target', target)]:
        if ref:
            try:
                refs[key] = git(cwd, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()
            except subprocess.CalledProcessError as exc:
                raise WorkflowError(f'Cannot resolve {key} commit') from exc
            add(key.encode())
            add(refs[key].encode())
    return {'sha256': h.hexdigest(), 'refs': refs}


class Journal:
    def __init__(self, cwd, session, root=None):
        if not session:
            raise WorkflowError('Supply the host session id with --session')
        self.cwd = canonical(cwd)
        self.session = session
        self.project_root = Path(root).resolve() if root else artifact_root(self.cwd)
        self.project_root.mkdir(parents=True, exist_ok=True)
        if self.project_root == self.cwd or self.cwd in self.project_root.parents:
            raise WorkflowError('Artifacts must be outside the worktree')
        self.db = sqlite3.connect(self.project_root / 'journal.sqlite3', timeout=15, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('CREATE TABLE IF NOT EXISTS tasks (worktree TEXT, session TEXT, data TEXT, PRIMARY KEY(worktree,session))')

    @property
    def root(self):
        task = self.load()
        key = task['id'] if task else 'pending-' + digest((str(self.cwd) + self.session).encode())[:20]
        path = self.project_root / 'tasks' / key
        path.mkdir(parents=True, exist_ok=True)
        return path

    def load(self):
        row = self.db.execute('SELECT data FROM tasks WHERE worktree=? AND session=?', (str(self.cwd), self.session)).fetchone()
        return json.loads(row['data']) if row else None

    def transaction(self, change):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            task = change(self.load())
            self.db.execute('INSERT OR REPLACE INTO tasks VALUES (?,?,?)', (str(self.cwd), self.session, json.dumps(task)))
            self.db.execute('COMMIT')
            return task
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def begin(self, kind, scope, base=None, target=None, pending=False, new=False):
        if kind in ('code-review', 'pr-review') and not pending and not (base and target):
            raise WorkflowError('Reviews require --base and --target, or --pending until resolved')
        def update(old):
            identity = (kind, scope, base, target, pending)
            if old and kind == 'discussion' and old['kind'] != 'discussion' and self.missing(old):
                raise WorkflowError('Finish the active checkpoint or obtain an explicit human override before discussion mode')
            if old and not new and tuple(old[k] for k in ('kind', 'scope', 'base', 'target', 'pending')) == identity:
                return old
            return dict(id=str(uuid.uuid4()), kind=kind, scope=scope, base=base, target=target,
                        pending=pending, worktree=str(self.cwd), session=self.session, receipts={}, overrides=[], stops=[])
        return self.transaction(update)

    def resolve(self, base, target):
        fingerprint(self.cwd, base, target)
        old = self.load()
        if not old or old['kind'] not in ('code-review', 'pr-review'):
            raise WorkflowError('Declare a review before resolving its target')
        return self.begin(old['kind'], old['scope'], base, target)

    def source(self, task):
        return fingerprint(self.cwd, task['base'], task['target'])

    def artifact(self, path):
        path = Path(path).expanduser().resolve()
        if self.root not in path.parents or path.suffix.lower() != '.html':
            raise WorkflowError(f'HTML must be inside {self.root}')
        return path

    def receipt(self, stage, path, present):
        path = self.artifact(path)
        data = path.read_bytes()
        if b'<html' not in data.lower() or b'<script' not in data.lower():
            raise WorkflowError('Receipt needs a rendered interactive HTML document')
        task = self.load()
        if not task or task['pending']:
            raise WorkflowError('Begin a task and resolve pending review targets first')
        allowed = {'implementation': ('plan', 'post'), 'plan': ('plan',), 'code-review': ('review',), 'pr-review': ('review',), 'discussion': ()}
        if stage not in allowed[task['kind']]:
            raise WorkflowError('Stage does not belong to the declared task')
        source = self.source(task)
        present(path)
        if digest(path.read_bytes()) != digest(data) or self.source(task) != source:
            raise WorkflowError('HTML or source changed during presentation; render again')
        def update(current):
            if current['id'] != task['id']:
                raise WorkflowError('Task changed during presentation')
            current['receipts'][stage] = dict(task=current['id'], stage=stage, scope=current['scope'],
                session=self.session, worktree=str(self.cwd), source=source, html=str(path), sha256=digest(data),
                delivery='viewer command returned success; no human approval', generator='visual-explainer@' + json.loads((Path(__file__).resolve().parents[1] / 'vendor/provenance.json').read_text())['revision'])
            return current
        return self.transaction(update)

    def missing(self, task=None, publish=False, editing=False):
        task = task or self.load()
        if not task:
            return ['post'] if publish else []
        if task['pending']:
            return ['resolve']
        stages = {'implementation': ['plan', 'post'], 'plan': ['plan'], 'code-review': ['review'], 'pr-review': ['review'], 'discussion': []}[task['kind']]
        if editing:
            stages = ['plan']
        if publish:
            stages = list(dict.fromkeys(stages + ['post']))
        needs_source = bool(task['overrides']) or any(stage != 'plan' and stage in task['receipts'] for stage in stages)
        source = self.source(task) if needs_source else None
        missing = []
        for stage in stages:
            override = any(o['stage'] == stage and o['source'] == source for o in task['overrides'])
            if override:
                continue
            receipt = task['receipts'].get(stage)
            if not receipt:
                missing.append(stage)
                continue
            path = Path(receipt['html'])
            valid = path.is_file() and digest(path.read_bytes()) == receipt['sha256']
            valid = valid and receipt['task'] == task['id'] and receipt['scope'] == task['scope']
            if stage != 'plan':
                valid = valid and receipt['source'] == source
            if not valid:
                missing.append(stage)
        return missing

    def override_from_human(self, stage, reason):
        def update(task):
            if not task:
                raise WorkflowError('Begin a task first')
            task['overrides'].append(dict(stage=stage, reason=reason, source=self.source(task), origin='UserPromptSubmit'))
            return task
        return self.transaction(update)
