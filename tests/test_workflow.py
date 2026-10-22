import json
import io
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'plugins/aataraxiaa'))
from visual_review.core import Journal, WorkflowError, fingerprint, git
from visual_review.hooks import handle, shell_kind, tool_kind


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        mode = patch.dict('os.environ', {'VISUAL_REVIEW_MODE': 'strict'})
        mode.start()
        self.addCleanup(mode.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'user.name', 'Test')
        (self.repo / 'code.txt').write_text('before\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'initial')
        self.git('remote', 'add', 'origin', 'https://github.com/owner/repo.git')
        self.store = self.root / 'artifacts'
        self.journal = Journal(self.repo, 'session-1', self.store)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args]).decode().strip()

    def begin(self, kind='implementation', **kw):
        return self.journal.begin(kind, 'Change behavior', **kw)

    def deliver(self, stage, journal=None):
        journal = journal or self.journal
        path = journal.root / (stage + '.html')
        path.write_text('<html><body><button>Details</button><script>document.title="Review"</script></body></html>')
        journal.receipt(stage, path, lambda _: None)
        return path

    def event(self, event, **kw):
        return handle(dict(cwd=str(self.repo), session_id='session-1', hook_event_name=event, **kw), self.store)

    def test_plan_survives_implementation_but_post_binds_all_source(self):
        self.begin()
        self.deliver('plan')
        (self.repo / 'code.txt').write_text('after\n')
        self.assertEqual(self.journal.missing(editing=True), [])
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post')
        self.assertEqual(self.journal.missing(publish=True), [])
        (self.repo / 'new.txt').write_text('untracked')
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post')
        self.git('add', 'new.txt')
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post')
        self.git('commit', '-qm', 'changed')
        self.assertEqual(self.journal.missing(), ['post'])

    def test_missing_deleted_and_changed_html(self):
        self.begin()
        self.assertEqual(self.journal.missing(), ['plan','post'])
        plan = self.deliver('plan')
        post = self.deliver('post')
        post.unlink()
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post')
        plan.write_text('<html>tampered<script></script></html>')
        self.assertEqual(self.journal.missing(), ['plan'])

    def test_scope_change_resets_both_checkpoints(self):
        self.begin()
        self.deliver('plan')
        self.deliver('post')
        self.journal.begin('implementation', 'Other behavior')
        self.assertEqual(self.journal.missing(), ['plan','post'])

    def test_ordinary_followup_preserves_pending_final(self):
        self.begin()
        self.deliver('plan')
        task = self.journal.load()['id']
        self.event('UserPromptSubmit', prompt='Also consider the empty case')
        self.assertEqual(self.journal.load()['id'], task)
        self.assertEqual(self.journal.missing(), ['post'])
        self.journal.begin('discussion', 'No visual')
        self.assertEqual(self.journal.missing(), [])

    def test_explicit_new_task_resets_plan(self):
        self.begin()
        self.deliver('plan')
        self.event('UserPromptSubmit', prompt='New task: implement another behavior')
        self.assertEqual(self.journal.missing(), ['plan','post'])

    def test_read_only_review_requires_pair_and_skips_empty_diff(self):
        with self.assertRaises(WorkflowError):
            self.begin('code-review')
        self.begin('code-review', pending=True)
        self.assertEqual(self.journal.missing(), ['resolve'])
        with self.assertRaises(WorkflowError):
            self.deliver('review')
        self.journal.resolve('HEAD', 'HEAD')
        self.assertEqual(self.journal.missing(), [])
        self.deliver('review')
        self.assertEqual(self.journal.missing(), [])
        (self.repo / 'code.txt').write_text('different')
        self.assertEqual(self.journal.missing(), [])

    def test_strict_stop_continues_only_once_per_task(self):
        self.begin()
        first = self.event('Stop')
        self.assertEqual(first['decision'], 'block')
        second = self.event('Stop', stop_hook_active=True)
        self.assertNotIn('decision', second)
        self.assertEqual(second, {})
        (self.repo / 'code.txt').write_text('changed')
        self.assertEqual(self.event('Stop'), {})

    def test_sessions_are_isolated_and_worktrees_share_task(self):
        self.begin()
        self.deliver('plan')
        self.deliver('post')
        other = Journal(self.repo, 'session-2', self.store)
        self.assertIsNone(other.load())
        self.assertEqual(other.missing(publish=True), ['post'])
        worktree = self.root / 'other'
        self.git('worktree', 'add', '--detach', str(worktree))
        separate = Journal(worktree, 'session-1', self.store)
        self.assertEqual(separate.load()['id'], self.journal.load()['id'])
        self.assertEqual(separate.missing(editing=True), [])

    def test_known_edits_block_until_plan_including_actual_codex_patch(self):
        event = self.event('PreToolUse', tool_name='apply_patch', tool_input={'command':'*** Begin Patch\n*** Update File: code.txt\n@@\n-before\n+after\n*** End Patch'})
        self.assertEqual(event['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('--session session-1', event['hookSpecificOutput']['permissionDecisionReason'])
        self.deliver('plan')
        self.assertEqual(self.event('PreToolUse', tool_name='Edit', tool_input={'file_path':str(self.repo / 'code.txt')}), {})

    def test_safe_reads_and_artifact_only_edits_allowed(self):
        self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command':'rg code . && git status --short && git show HEAD:code.txt'}), {})
        self.assertEqual(shell_kind('git show commit', self.journal), 'read')
        self.assertEqual(tool_kind({'tool_name':'apply_patch','tool_input':{'command':'*** Add File: '+str(self.journal.root / 'page.src.html')+'\n+text'}}, self.journal), 'artifact')
        self.assertEqual(shell_kind('touch '+str(self.journal.root / 'new.html'), self.journal), 'read')
        self.assertEqual(shell_kind('touch code.txt', self.journal), 'write')
        self.assertEqual(shell_kind('python3 -c "print(1)"', self.journal), 'read')
        self.assertEqual(shell_kind('echo visual-review; rm code.txt', self.journal), 'write')

    def test_publication_blocks_without_task_and_chained_gh_and_mcp(self):
        for name, payload in [('Bash', {'command':'git status && gh --repo owner/repo pr create --title test'}),
                              ('exec_command', {'cmd':'printf ok; gh pr create --draft'}),
                              ('mcp__github__create_pull_request', {'title':'test'})]:
            with self.subTest(name=name):
                answer = self.event('PreToolUse', tool_name=name, tool_input=payload)
                self.assertEqual(answer['hookSpecificOutput']['permissionDecision'], 'deny')
        self.deliver('plan')
        self.deliver('post')
        self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command':'gh pr create --draft'}), {})
        (self.repo / 'code.txt').write_text('changed')
        self.assertEqual(self.event('PreToolUse', tool_name='mcp__github__create_pull_request', tool_input={})['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_failed_presentation_records_nothing(self):
        self.begin()
        path = self.journal.root / 'page.html'
        path.write_text('<html><script></script></html>')
        def fail(_):
            raise OSError('viewer failed')
        with self.assertRaises(OSError):
            self.journal.receipt('plan', path, fail)
        self.assertEqual(self.journal.missing(editing=True), ['plan'])

    def test_artifacts_cannot_escape_or_replace_source(self):
        self.begin()
        with self.assertRaises(WorkflowError):
            self.journal.receipt('plan', self.repo / 'page.html', lambda _:None)
        link = self.store / 'escape.html'
        link.symlink_to(self.repo / 'code.txt')
        with self.assertRaises(WorkflowError):
            self.journal.artifact(link)

    def test_human_override_is_fingerprint_bound_and_audited(self):
        self.begin()
        self.event('UserPromptSubmit', prompt='visual-review override plan: urgent explicit exception')
        self.assertEqual(self.journal.missing(editing=True), [])
        self.assertEqual(self.journal.load()['overrides'][0]['origin'], 'UserPromptSubmit')
        (self.repo / 'code.txt').write_text('changed')
        self.assertEqual(self.journal.missing(editing=True), ['plan'])

    def test_dirty_env_is_not_read_or_certified(self):
        def fake_git(cwd, *args, **kwargs):
            if args[0] == 'status':
                return b'?? .env\0'
            return git(cwd, *args, **kwargs)
        with patch('visual_review.core.git', side_effect=fake_git), patch.object(Path, 'read_bytes', side_effect=AssertionError('read forbidden')):
            with self.assertRaisesRegex(WorkflowError, 'never read'):
                fingerprint(self.repo)

    def test_worktree_uses_session_plan_and_refreshes_result(self):
        self.begin()
        self.deliver('plan')
        self.deliver('post')
        other = self.root / 'other'
        self.git('worktree', 'add', '-b', 'other', str(other))
        result = self.event('PreToolUse', tool_name='Edit', tool_input={'file_path': str(other / 'code.txt')})
        self.assertEqual(result, {})
        self.assertEqual(self.journal.missing(), ['post'])
        foreign = Journal(other, 'session-1', self.store)
        self.assertEqual(foreign.load()['id'], self.journal.load()['id'])
        self.deliver('post')
        (other / 'code.txt').write_text('changed')
        self.assertEqual(self.journal.missing(), ['post'])
        handle(dict(cwd=str(other), session_id='session-1', hook_event_name='UserPromptSubmit',
                    prompt='visual-review override post: skip this one'), self.store)
        self.assertEqual(self.journal.missing(), [])

    def test_publication_identity(self):
        self.begin()
        self.deliver('plan')
        self.deliver('post')
        branch = self.git('branch', '--show-current')
        for payload in ({'command': 'gh pr create -R owner/other'}, {'command': 'gh pr create --head other'}):
            self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input=payload)['hookSpecificOutput']['permissionDecision'], 'deny')
        payload = {'owner': 'owner', 'repo': 'repo', 'head': branch}
        self.assertEqual(self.event('PreToolUse', tool_name='mcp__github__create_pull_request', tool_input=payload), {})
        payload['head'] = 'other'
        self.assertEqual(self.event('PreToolUse', tool_name='mcp__github__create_pull_request', tool_input=payload)['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_task_html_isolation(self):
        self.begin()
        first = self.deliver('plan')
        another = Journal(self.repo, 'another', self.store)
        another.begin('implementation', 'Other')
        second = self.deliver('plan', another)
        self.assertNotEqual(first, second)
        second.write_text('changed')
        self.assertEqual(self.journal.missing(editing=True), [])
        self.begin(new=True)
        self.assertNotEqual(first.parent, self.journal.root)

    def test_status_and_repair_use_current_task_directory(self):
        from visual_review.cli import main
        self.begin()
        output = io.StringIO()
        with patch('visual_review.cli.Journal', return_value=self.journal), redirect_stdout(output):
            self.assertEqual(main(['--cwd', str(self.repo), '--session', 'session-1', 'status']), 0)
        self.assertEqual(json.loads(output.getvalue())['artifacts'], str(self.journal.root))
        result = self.event('PreToolUse', tool_name='Edit', tool_input={'file_path': str(self.repo / 'code.txt')})
        self.assertIn(str(self.journal.root / 'plan.src.html'), result['hookSpecificOutput']['permissionDecisionReason'])

    def test_stash_inspection_preserves_review(self):
        self.begin('code-review', base='HEAD', target='HEAD')
        self.deliver('review')
        before = self.journal.load()
        for cmd in ('git stash list', 'git stash show -p'):
            self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command': cmd}), {})
            self.assertEqual(self.journal.load(), before)
        self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command': 'git stash push'}), {})

    def test_fingerprint_reads_only_changed_content(self):
        initial = fingerprint(self.repo)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('clean content read')):
            self.assertEqual(fingerprint(self.repo), initial)
        (self.repo / 'code.txt').write_text('changed')
        changed = fingerprint(self.repo)
        self.assertNotEqual(initial, changed)
        (self.repo / 'code.txt').write_text('changed again')
        self.assertNotEqual(changed, fingerprint(self.repo))
        (self.repo / 'code.txt').unlink()
        self.assertNotEqual(changed, fingerprint(self.repo))

    def test_dirty_publication_requires_commit_and_new_visual(self):
        self.begin()
        self.deliver('plan')
        (self.repo / 'code.txt').write_text('dirty')
        self.deliver('post')
        event = dict(tool_name='Bash', tool_input={'command': 'gh pr create'})
        self.assertIn('Commit', self.event('PreToolUse', **event)['hookSpecificOutput']['permissionDecisionReason'])
        self.git('add', '.')
        self.git('commit', '-qm', 'implementation')
        self.assertEqual(self.event('PreToolUse', **event)['hookSpecificOutput']['permissionDecision'], 'deny')
        self.deliver('post')
        self.assertEqual(self.event('PreToolUse', **event), {})

    def test_symlink_hashes_link_not_destination(self):
        outside = self.root / 'outside.txt'
        outside.write_text('private')
        link = self.repo / 'link'
        link.symlink_to(outside)
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('followed link')):
            first = fingerprint(self.repo)
            outside.write_text('other private content')
            self.assertEqual(first, fingerprint(self.repo))
            link.unlink()
            link.symlink_to(self.root / 'different')
            self.assertNotEqual(first, fingerprint(self.repo))

    def test_dirty_submodule_content_and_uninitialized_path(self):
        source = self.root / 'sub-source'
        subprocess.run(['git', 'clone', '-q', str(self.repo), str(source)], check=True)
        self.git('-c', 'protocol.file.allow=always', 'submodule', 'add', '-q', str(source), 'child')
        self.git('commit', '-qam', 'submodule')
        first = fingerprint(self.repo)
        (self.repo / 'child/code.txt').write_text('changed')
        second = fingerprint(self.repo)
        self.assertNotEqual(first, second)
        (self.repo / 'child/code.txt').write_text('changed again')
        self.assertNotEqual(second, fingerprint(self.repo))
        self.git('submodule', 'deinit', '-f', 'child')
        fingerprint(self.repo)

    def test_advisory_never_denies_or_continues_and_reminds_once(self):
        with patch.dict('os.environ', {}, clear=True):
            self.assertEqual(self.event('PreToolUse', tool_name='Edit', tool_input={'file_path':str(self.repo / 'code.txt')}), {})
            self.assertIsNone(self.journal.load())
            self.assertEqual(self.event('Stop'), {})
            self.begin()
            for name, payload in [('Edit', {'file_path':str(self.repo / 'code.txt')}), ('Bash', {'command':'gh pr create -R unknown/repo'})]:
                self.assertEqual(self.event('PreToolUse', tool_name=name, tool_input=payload), {})
            first = self.event('Stop')
            self.assertNotIn('decision', first)
            self.assertIn('Optional', first['systemMessage'])
            self.assertEqual(self.event('Stop'), {})

    def test_exempt_reads_redirects_artifact_root_scratch_and_config(self):
        for cmd in ('grep x code.txt 2>/dev/null', 'git -c color.ui=false diff', 'echo hello > scratch.txt'):
            self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command':cmd}), {})
        for path in (self.store / 'plan.src.html', self.store / 'tasks/older/plan.src.html',
                     self.repo / 'scratch/note.txt', self.repo / 'work/notes.md',
                     Path.home() / '.claude/settings.json', Path.home() / '.codex/config.toml',
                     self.root / 'temporary.txt'):
            self.assertEqual(self.event('PreToolUse', tool_name='Write', tool_input={'file_path':str(path)}), {})
        self.assertIsNone(self.journal.load())

    def test_bot_notice_and_empty_review_do_not_request_pages(self):
        self.assertEqual(self.event('UserPromptSubmit', prompt='CI event: review-bot notice for pull request 123'), {})
        self.assertEqual(self.event('Stop'), {})
        self.begin('pr-review', pending=True)
        self.assertEqual(self.event('Stop'), {})
        self.journal.resolve('HEAD', 'HEAD')
        self.assertEqual(self.event('Stop'), {})


    def test_session_routing_survives_new_journal_from_sibling(self):
        home = self.root / 'home'
        home.mkdir()
        other = self.root / 'other'
        self.git('worktree', 'add', '--detach', str(other))
        with patch.object(Path, 'home', return_value=home), patch('visual_review.core.artifact_root', return_value=self.store) as artifacts:
            first = Journal(self.repo, 'routing-session')
            first.begin('implementation', 'Shared request')
            self.deliver('plan', first)
            second = Journal(other, 'routing-session')
            self.assertEqual(first.load()['id'], second.load()['id'])
            self.assertEqual(second.missing(editing=True), [])
            artifacts.assert_called_once()


    def test_hook_infrastructure_error_does_not_deny_even_in_strict_mode(self):
        from visual_review.cli import main
        output = io.StringIO()
        event = dict(cwd=str(self.repo), session_id='session-1', hook_event_name='PreToolUse', tool_name='Bash', tool_input={'command':'grep x code.txt 2>/dev/null'})
        with patch('visual_review.cli.handle', side_effect=OSError('store unavailable')), patch('sys.stdin', io.StringIO(json.dumps(event))), redirect_stdout(output):
            self.assertEqual(main(['hook']), 0)
        result = json.loads(output.getvalue())
        self.assertNotIn('hookSpecificOutput', result)
        self.assertIn('Continuing', result['systemMessage'])



if __name__ == '__main__':
    unittest.main()
