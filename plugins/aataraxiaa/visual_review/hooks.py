"""Host hook protocol and intentionally bounded command recognition."""
import json
from pathlib import Path
import re
import shlex
from .core import Journal, WorkflowError, digest

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


def inside_artifacts(path, journal, cwd=None):
    try:
        resolved = (Path(cwd or journal.cwd) / path).resolve()
        return journal.root in resolved.parents
    except (OSError, ValueError):
        return False


def shell_kind(text, journal):
    """Recognize direct known writes/publishing. Opaque programs are not parsed."""
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=';&|<>\n')
        lexer.whitespace = ' \t\r'
        lexer.whitespace_split = True
        lexer.commenters = '#'
        tokens = list(lexer)
    except ValueError:
        return 'unknown'
    segments, segment = [], []
    for token in tokens:
        if token and all(c in ';&|\n' for c in token):
            if segment:
                segments.append(segment); segment = []
        else:
            segment.append(token)
    if segment:
        segments.append(segment)
    result = 'read'
    cwd = journal.cwd
    for words in segments:
        while words and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', words[0]):
            words = words[1:]
        if not words:
            continue
        if words[0] == 'env':
            words = words[1:]
            while words and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', words[0]):
                words = words[1:]
        if not words:
            continue
        exe = Path(words[0]).name
        args = words[1:]
        if exe == 'cd' and args:
            cwd = (cwd / args[0]).resolve(); continue
        if exe == 'gh':
            # Global flags such as --repo may precede the subcommand.
            if any(args[i:i+2] == ['pr', 'create'] for i in range(len(args)-1)):
                return 'publish'
        redirects = [args[i+1] for i, a in enumerate(args[:-1]) if a in ('>', '>>', '>|', '&>')]
        if redirects and not all(inside_artifacts(p, journal, cwd) for p in redirects):
            result = 'write'
        if exe in ('python', 'python3') and args and Path(args[0]).resolve() == CLI:
            # Only this executable and structured companion operations are exempt.
            continue
        if exe in ('rm', 'mkdir', 'rmdir', 'touch', 'tee', 'truncate', 'chmod', 'chown', 'mv', 'cp', 'install'):
            paths = [a for a in args if not a.startswith('-')]
            if not paths or not all(inside_artifacts(p, journal, cwd) for p in paths):
                result = 'write'
        elif exe in ('sed', 'perl') and any(a.startswith('-i') for a in args):
            result = 'write'
        elif exe == 'git':
            mutators = {'add','commit','checkout','switch','reset','restore','merge','rebase','cherry-pick','revert','clean','apply','am','stash','mv','rm','update-index'}
            git_args = list(args)
            while git_args and git_args[0].startswith('-'):
                flag = git_args.pop(0)
                if flag in ('-C', '-c', '--git-dir', '--work-tree') and git_args:
                    git_args.pop(0)
            if git_args and git_args[0] in mutators:
                result = 'write'
        elif exe in ('npm', 'pnpm', 'yarn', 'bun', 'pip', 'pip3') and any(a in ('install','add','remove','uninstall','update') for a in args):
            result = 'write'
        elif exe in ('apply_patch', 'patch'):
            result = 'write'
    return result


def tool_kind(event, journal):
    name = event.get('tool_name', '')
    payload = event.get('tool_input') or {}
    if not isinstance(payload, dict):
        payload = {'command': payload}
    lower = name.lower()
    if ('github' in lower and re.search(r'create_?pull_?request|create_pull_request', lower)) or lower.endswith('__create_pr'):
        return 'publish'
    if name in ('Bash', 'exec_command', 'functions.exec_command') or lower.endswith('__exec_command'):
        return shell_kind(payload.get('command', payload.get('cmd', '')), journal)
    if name in ('apply_patch', 'functions.apply_patch'):
        patch = payload.get('command', payload.get('patch', ''))
        paths = re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', patch, re.M)
        return 'artifact' if paths and all(inside_artifacts(p, journal) for p in paths) else 'write'
    if name in ('Write', 'Edit', 'MultiEdit') or lower.endswith(('__write_file', '__edit_file')):
        path = payload.get('file_path', payload.get('path', ''))
        return 'artifact' if path and inside_artifacts(path, journal) else 'write'
    return 'unknown'


def detect(prompt):
    lowered = prompt.lower().strip()
    lowered = re.sub(r'^new task:\s*', '', lowered)
    if re.search(r'\b(?:review|critique|audit)\b.*\b(?:pull request|pr\b)', lowered):
        return 'pr-review'
    if re.search(r'\b(?:review|critique|audit)\b.*\b(?:code|diff|changes|commit)\b', lowered):
        return 'code-review'
    if re.match(r'(?:please\s+)?(?:make|write|create|give me|draft)\s+(?:a\s+)?(?:implementation\s+)?plan\b', lowered) or lowered.startswith('plan '):
        return 'plan'
    if re.match(r'(?:please\s+)?(?:implement|fix|refactor|build|add|remove|change|update)\b', lowered):
        return 'implementation'
    return None


def context(event, message):
    return {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': message}}


def handle(event, root=None):
    journal = Journal(event.get('cwd', '.'), event.get('session_id', ''), root=root)
    kind = event.get('hook_event_name')
    if kind == 'SessionStart':
        return context(kind, 'Use visual-review for implementation, plans, code reviews and PR reviews. ' +
            'Before editing, present an interactive plan; after implementation present the actual result. ' +
            'Reviews need explicit base/target commits. Before PR creation a current post visual is mandatory. ' +
            'Discussion and inspection do not need visuals. Start with ' + command(journal, 'status') +
            '. Workflow skill: ' + str(CLI.parents[1] / 'skills/visual-review/SKILL.md'))
    if kind == 'UserPromptSubmit':
        prompt = event.get('prompt', '')
        # Only an actual human prompt can record an override. Hook-generated Stop
        # continuations have stop_hook_active, and never authorize exceptions.
        override = re.fullmatch(r'visual-review override (plan|post|review):\s*(\S[\s\S]*)', prompt.strip())
        if override and not event.get('stop_hook_active'):
            journal.override_from_human(*override.groups())
            return context(kind, 'Recorded explicit human visual-review override for this source fingerprint. It is not approval of the code.')
        detected = detect(prompt)
        current = journal.load()
        if detected and (not current or not journal.missing(current) or prompt.lower().startswith('new task:')):
            journal.begin(detected, prompt.strip(), pending=detected in ('code-review', 'pr-review'), new=True)
        if detected or (current and journal.missing(current)):
            return context(kind, repair(journal, journal.missing()))
        return {}
    if kind == 'PreToolUse':
        operation = tool_kind(event, journal)
        if operation not in ('write', 'publish'):
            return {}
        task = journal.load()
        if (operation == 'write' or operation == 'publish') and (not task or task['kind'] != 'implementation'):
            journal.begin('implementation', task['scope'] if task else 'Implementation detected by edit hook')
        missing = journal.missing(publish=operation == 'publish', editing=operation == 'write')
        if missing:
            return {'hookSpecificOutput': {'hookEventName': kind, 'permissionDecision': 'deny', 'permissionDecisionReason': repair(journal, missing)}}
        return {}
    if kind == 'Stop':
        task = journal.load()
        missing = journal.missing(task)
        if not missing:
            return {}
        marker = digest(json.dumps([missing, journal.source(task)], sort_keys=True).encode())
        if marker in task['stops']:
            return {'systemMessage': 'Visual-review workflow INCOMPLETE. ' + repair(journal, missing)}
        def update(current):
            current['stops'].append(marker)
            return current
        journal.transaction(update)
        return {'decision': 'block', 'reason': repair(journal, missing)}
    return {}
