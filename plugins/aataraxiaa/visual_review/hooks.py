import json
import os
from pathlib import Path
import re
import shlex
from .core import Journal, WorkflowError, digest, canonical, git

CLI = Path(__file__).resolve().parents[1] / 'scripts/visual-review'


def command(journal, *args):
    return shlex.join(['python3', str(CLI), '--cwd', str(journal.cwd), '--session', journal.session, *args])


def repair(journal, missing):
    task = journal.load()
    steps = []
    if not task:
        steps.append(command(journal, 'begin', '--kind', 'implementation', '--scope', 'Describe the requested change'))
    if 'resolve' in missing:
        steps.append(command(journal, 'resolve', '--base', 'BASE_COMMIT', '--target', 'TARGET_COMMIT'))
    else:
        for stage in missing:
            steps.append(command(journal, 'render', '--stage', stage, '--source', str(journal.root / (stage + '.src.html')), '--present'))
    return ('Visual review required. Read ' + str(CLI.parents[1] / 'skills/visual-review/SKILL.md') +
            '. Author interactive HTML from the actual scope/diff, then run: ' + '; '.join(steps) +
            '. Receipts prove presentation, never human approval.')


def strict_mode():
    return os.environ.get('VISUAL_REVIEW_MODE', 'advisory') == 'strict'


def inside_artifacts(path, journal, cwd=None):
    resolved = (Path(cwd or journal.cwd) / path).expanduser().resolve()
    return resolved == journal.project_root or journal.project_root in resolved.parents or 'review-artifacts' in resolved.parts


def source_file(path, journal, cwd):
    path = (Path(cwd) / path).expanduser().resolve()
    if inside_artifacts(path, journal):
        return False
    homes = [Path.home() / name for name in ('.claude', '.codex', '.agents', '.config')]
    if any(path == home or home in path.parents for home in homes):
        return False
    root = canonical(path.parent)
    if not (root / '.git').exists():
        return False
    relative = path.relative_to(root)
    if any(part in ('tmp', 'temp', 'scratch', 'work', '.git', 'node_modules', '.claude', '.codex') for part in relative.parts):
        return False
    return subprocess_ignored(root, relative) is False


def subprocess_ignored(root, relative):
    return bool(git(root, 'check-ignore', str(relative), check=False).strip())


def repository_id(value):
    value = re.sub(r'^(?:https?://|ssh://git@|git@)', '', value).rstrip('/')
    value = value.replace('github.com:', 'github.com/')
    value = value.removesuffix('.git')
    return value if value.count('/') == 2 else 'github.com/' + value


def publication(cwd, repository=None, head=None, required=False):
    from .core import git
    if not strict_mode():
        return ('publish', cwd)
    remote = git(cwd, 'remote', 'get-url', 'origin', check=False).decode().strip()
    branch = git(cwd, 'symbolic-ref', '--short', 'HEAD', check=False).decode().strip()
    if not remote or not branch or (required and (not repository or not head)):
        raise WorkflowError('PR target requires a local origin and current branch, plus explicit repository/head for MCP')
    if repository and repository_id(repository) != repository_id(remote):
        raise WorkflowError('PR repository differs from the reviewed worktree origin')
    if head and head != branch:
        raise WorkflowError('PR head differs from the reviewed worktree branch')
    if git(cwd, 'status', '--porcelain=v1', '--untracked-files=all', '--ignore-submodules=none').strip():
        raise WorkflowError('Commit the implementation, then refresh the post visual before PR creation')
    return ('publish', cwd)


def shell_actions(text, journal, cwd):
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=';&|<>\n')
        lexer.whitespace = ' \t\r'
        lexer.whitespace_split = True
        lexer.commenters = '#'
        tokens = list(lexer)
    except ValueError as exc:
        return []
    segments, segment = [], []
    for token in tokens:
        if token and all(c in ';&|\n' for c in token):
            if segment:
                segments.append(segment)
                segment = []
        else:
            segment.append(token)
    if segment:
        segments.append(segment)
    actions = []
    def write(path, directory=False):
        if any(c in path for c in '$`*?[]~'):
            return
        resolved = (cwd / path).resolve()
        if source_file(resolved, journal, cwd):
            actions.append(('write', resolved if directory else resolved.parent))
    for words in segments:
        if words and words[0] == 'env':
            words = words[1:]
        while words and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', words[0]):
            if words[0].split('=', 1)[0] in ('GH_REPO', 'GH_HOST', 'GIT_DIR', 'GIT_WORK_TREE'):
                return []
            words = words[1:]
        if not words:
            continue
        exe, args = Path(words[0]).name, words[1:]
        if exe == 'cd':
            if len(args) != 1 or any(c in args[0] for c in '$`~'):
                return []
            cwd = (cwd / args[0]).resolve()
            continue
        if exe in ('python', 'python3') and args and (cwd / args[0]).resolve() == CLI:
            continue
        if exe == 'gh' and any(args[i:i+2] == ['pr', 'create'] for i in range(len(args)-1)):
            def option(*flags):
                for i, value in enumerate(args):
                    for flag in flags:
                        if value == flag:
                            if i+1 == len(args):
                                raise WorkflowError('Missing publication option')
                            return args[i+1]
                        if len(flag) == 2 and value.startswith(flag) and value != flag:
                            return value[2:]
                        if value.startswith(flag + '='):
                            return value.split('=', 1)[1]
                return None
            actions.append(publication(cwd, option('--repo', '-R'), option('--head', '-H')))
        elif exe == 'git':
            git_cwd = cwd
            while args and args[0].startswith('-'):
                flag = args.pop(0)
                if flag in ('--no-pager', '--no-optional-locks'):
                    continue
                if flag == '-C' and args:
                    git_cwd = (git_cwd / args.pop(0)).resolve()
                else:
                    break
            mutators = {'add','commit','checkout','switch','reset','restore','merge','rebase','cherry-pick','revert','clean','apply','am','stash','mv','rm','update-index'}
            read_stash = args[:2] in (['stash', 'list'], ['stash', 'show'])
            if args and args[0] in mutators and not read_stash:
                pass
        elif exe in ('rm', 'mkdir', 'rmdir', 'touch', 'tee', 'truncate', 'chmod', 'chown', 'mv', 'cp', 'install'):
            paths = [a for a in args if not a.startswith('-')]
            if not paths:
                continue
            for path in (paths[-1:] if exe in ('cp', 'install') else paths):
                write(path)
        elif exe in ('sed', 'perl') and any(a.startswith('-i') for a in args):
            continue
        elif exe in ('npm', 'pnpm', 'yarn', 'bun', 'pip', 'pip3') and any(a in ('install','add','remove','uninstall','update') for a in args):
            continue
        elif exe in ('apply_patch', 'patch'):
            continue
    return actions


def tool_actions(event, journal):
    name = event.get('tool_name', '')
    payload = event.get('tool_input') or {}
    if not isinstance(payload, dict):
        payload = {'command': payload}
    cwd = (Path(event.get('cwd', '.')) / payload.get('workdir', '.')).resolve()
    lower = name.lower()
    if ('github' in lower and re.search(r'create_?pull_?request', lower)) or lower.endswith('__create_pr'):
        repository = payload.get('repository', payload.get('repo', payload.get('repo_name')))
        if repository and payload.get('owner'):
            repository = payload['owner'] + '/' + repository
        return [publication(cwd, repository, payload.get('head'), required=True)]
    if name in ('Bash', 'exec_command', 'functions.exec_command') or lower.endswith('__exec_command'):
        return shell_actions(payload.get('command', payload.get('cmd', '')), journal, cwd)
    if name in ('apply_patch', 'functions.apply_patch'):
        patch = payload.get('command', payload.get('patch', ''))
        paths = re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', patch, re.M)
    elif name in ('Write', 'Edit', 'MultiEdit') or lower.endswith(('__write_file', '__edit_file')):
        paths = [payload.get('file_path', payload.get('path', ''))]
    else:
        return []
    if not paths or not all(paths):
        raise WorkflowError('Cannot resolve edit targets')
    return [('write', (cwd / path).resolve().parent) for path in paths if source_file(path, journal, cwd)]


def shell_kind(text, journal):
    actions = shell_actions(text, journal, journal.cwd)
    return 'publish' if any(a[0] == 'publish' for a in actions) else 'write' if actions else 'read'


def tool_kind(event, journal):
    actions = tool_actions(event, journal)
    return actions[0][0] if actions else 'artifact'


def detect(prompt):
    if prompt.lower().startswith('new task:') and re.match(r'(?:implement|fix|refactor|build|add|remove|change|update)\b', prompt.split(':', 1)[1].strip().lower()):
        return 'implementation'
    lowered = re.sub(r'^new task:\s*', '', prompt.lower().strip())
    if re.match(r'(?:please\s+)?(?:review|critique|audit)\s+(?:the\s+)?(?:pull request|pr\b)', lowered):
        return 'pr-review'
    if re.match(r'(?:please\s+)?(?:review|critique|audit)\s+(?:the\s+)?(?:code|diff|changes|commit)', lowered):
        return 'code-review'
    if re.match(r'(?:please\s+)?(?:make|write|create|give me|draft)\s+(?:a\s+)?(?:implementation\s+)?plan\b', lowered) or lowered.startswith('plan '):
        return 'plan'
    return None


def context(event, message):
    return {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': message}}


def handle(event, root=None):
    journal = Journal(event.get('cwd', '.'), event.get('session_id', ''), root=root)
    kind = event.get('hook_event_name')
    if kind == 'SessionStart':
        return context(kind, 'Use visual-review for implementation, plans, code reviews and PR reviews. ' +
            'Offer a concise visual for meaningful work; routine reads and small edits need none. ' +
            'Default mode is advisory: never stop work to produce a page. Strict gates require VISUAL_REVIEW_MODE=strict. ' +
            'Discussion and inspection do not need visuals. Start with ' + command(journal, 'status') +
            '. Workflow skill: ' + str(CLI.parents[1] / 'skills/visual-review/SKILL.md'))
    if kind == 'UserPromptSubmit':
        prompt = event.get('prompt', '')
        override = re.fullmatch(r'visual-review override (plan|post|review):\s*(\S[\s\S]*)', prompt.strip())
        if override and not event.get('stop_hook_active'):
            journal.override_from_human(*override.groups())
            return context(kind, 'Recorded explicit human visual-review override for this source fingerprint. It is not approval of the code.')
        detected = detect(prompt)
        current = journal.load()
        if detected and (not current or not journal.missing(current) or prompt.lower().startswith('new task:')):
            journal.begin(detected, prompt.strip(), pending=detected in ('code-review', 'pr-review'), new=True)
        if detected and strict_mode():
            return context(kind, repair(journal, journal.missing()))
        return {}
    if kind == 'PreToolUse':
        try:
            actions = tool_actions(event, journal)
            for operation, target in actions:
                target = target.resolve()
                while not target.exists() and target != target.parent:
                    target = target.parent
                task = journal.load()
                if not task:
                    if not strict_mode():
                        continue
                    journal.begin('implementation', 'Implementation explicitly gated in strict mode')
                journal.include_target(target)
                if not strict_mode():
                    continue
                missing = journal.missing(publish=operation == 'publish', editing=operation == 'write')
                if missing:
                    raise WorkflowError(repair(journal, missing))
        except WorkflowError as exc:
            if not strict_mode():
                return {}
            return {'hookSpecificOutput': {'hookEventName': kind, 'permissionDecision': 'deny', 'permissionDecisionReason': str(exc)}}
        return {}
    if kind == 'Stop':
        task = journal.load()
        missing = journal.missing(task)
        if not missing:
            return {}
        if task['pending']:
            return {}
        marker = 'reminded'
        if marker in task['stops']:
            return {}
        def update(current):
            current['stops'].append(marker)
            return current
        journal.transaction(update)
        if strict_mode():
            return {'decision': 'block', 'reason': repair(journal, missing)}
        return {'systemMessage': 'Optional visual review: offer a concise page if it would help explain this work. Do not continue solely to produce one.'}
    return {}
