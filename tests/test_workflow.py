import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'plugins/aataraxiaa'))
from visual_review.core import Journal, WorkflowError
from visual_review.hooks import handle, shell_kind, tool_kind


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'; self.repo.mkdir()
        self.git('init', '-q'); self.git('config', 'user.email', 'test@example.com'); self.git('config', 'user.name', 'Test')
        (self.repo / 'code.txt').write_text('before\n')
        self.git('add', '.'); self.git('commit', '-qm', 'initial')
        self.store = self.root / 'artifacts'
        self.journal = Journal(self.repo, 'session-1', self.store)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args]).decode().strip()

    def begin(self, kind='implementation', **kw):
        return self.journal.begin(kind, 'Change behavior', **kw)

    def deliver(self, stage, journal=None):
        journal = journal or self.journal
        path = self.store / (stage + '.html')
        path.write_text('<html><body><button>Details</button><script>document.title="Review"</script></body></html>')
        journal.receipt(stage, path, lambda _: None)
        return path

    def event(self, event, **kw):
        return handle(dict(cwd=str(self.repo), session_id='session-1', hook_event_name=event, **kw), self.store)

    def test_plan_survives_implementation_but_post_binds_all_source(self):
        self.begin(); self.deliver('plan')
        (self.repo / 'code.txt').write_text('after\n')
        self.assertEqual(self.journal.missing(editing=True), [])
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post')
        self.assertEqual(self.journal.missing(publish=True), [])
        (self.repo / 'new.txt').write_text('untracked')
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post'); self.git('add', 'new.txt')
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post'); self.git('commit', '-qm', 'changed')
        self.assertEqual(self.journal.missing(), ['post'])

    def test_missing_deleted_and_changed_html(self):
        self.begin()
        self.assertEqual(self.journal.missing(), ['plan','post'])
        plan = self.deliver('plan'); post = self.deliver('post')
        post.unlink()
        self.assertEqual(self.journal.missing(), ['post'])
        self.deliver('post'); plan.write_text('<html>tampered<script></script></html>')
        self.assertEqual(self.journal.missing(), ['plan'])

    def test_scope_change_resets_both_checkpoints(self):
        self.begin(); self.deliver('plan'); self.deliver('post')
        self.journal.begin('implementation', 'Other behavior')
        self.assertEqual(self.journal.missing(), ['plan','post'])

    def test_ordinary_followup_preserves_pending_final(self):
        self.begin(); self.deliver('plan')
        task = self.journal.load()['id']
        self.event('UserPromptSubmit', prompt='Also consider the empty case')
        self.assertEqual(self.journal.load()['id'], task)
        self.assertEqual(self.journal.missing(), ['post'])
        with self.assertRaises(WorkflowError):
            self.journal.begin('discussion', 'No visual')

    def test_explicit_new_task_resets_plan(self):
        self.begin(); self.deliver('plan')
        self.event('UserPromptSubmit', prompt='New task: implement another behavior')
        self.assertEqual(self.journal.missing(), ['plan','post'])

    def test_read_only_review_requires_explicit_resolved_pair(self):
        with self.assertRaises(WorkflowError):
            self.begin('code-review')
        self.begin('code-review', pending=True)
        self.assertEqual(self.journal.missing(), ['resolve'])
        with self.assertRaises(WorkflowError):
            self.deliver('review')
        self.journal.resolve('HEAD', 'HEAD')
        self.assertEqual(self.journal.missing(), ['review'])
        self.deliver('review')
        self.assertEqual(self.journal.missing(), [])
        (self.repo / 'code.txt').write_text('different')
        self.assertEqual(self.journal.missing(), ['review'])

    def test_stop_continues_once_then_visible_incomplete(self):
        self.begin()
        first = self.event('Stop')
        self.assertEqual(first['decision'], 'block')
        second = self.event('Stop', stop_hook_active=True)
        self.assertNotIn('decision', second)
        self.assertIn('INCOMPLETE', second['systemMessage'])
        (self.repo / 'code.txt').write_text('changed')
        self.assertEqual(self.event('Stop')['decision'], 'block')

    def test_sessions_and_worktrees_do_not_share_receipts(self):
        self.begin(); self.deliver('plan'); self.deliver('post')
        other = Journal(self.repo, 'session-2', self.store)
        self.assertIsNone(other.load())
        self.assertEqual(other.missing(publish=True), ['post'])
        worktree = self.root / 'other'
        self.git('worktree', 'add', '--detach', str(worktree))
        separate = Journal(worktree, 'session-1', self.store)
        self.assertIsNone(separate.load())
        self.assertEqual(separate.missing(publish=True), ['post'])

    def test_known_edits_block_until_plan_including_actual_codex_patch(self):
        event = self.event('PreToolUse', tool_name='apply_patch', tool_input={'command':'*** Begin Patch\n*** Update File: code.txt\n@@\n-before\n+after\n*** End Patch'})
        self.assertEqual(event['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('--session session-1', event['hookSpecificOutput']['permissionDecisionReason'])
        self.deliver('plan')
        self.assertEqual(self.event('PreToolUse', tool_name='Edit', tool_input={'file_path':str(self.repo / 'code.txt')}), {})

    def test_safe_reads_and_artifact_only_edits_allowed(self):
        self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command':'rg code . && git status --short && git show HEAD:code.txt'}), {})
        self.assertEqual(shell_kind('git show commit', self.journal), 'read')
        self.assertEqual(tool_kind({'tool_name':'apply_patch','tool_input':{'command':'*** Add File: '+str(self.store / 'page.src.html')+'\n+text'}}, self.journal), 'artifact')
        self.assertEqual(shell_kind('touch '+str(self.store / 'new.html'), self.journal), 'read')
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
        self.deliver('plan'); self.deliver('post')
        self.assertEqual(self.event('PreToolUse', tool_name='Bash', tool_input={'command':'gh pr create --draft'}), {})
        (self.repo / 'code.txt').write_text('changed')
        self.assertEqual(self.event('PreToolUse', tool_name='mcp__github__create_pull_request', tool_input={})['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_failed_presentation_records_nothing(self):
        self.begin()
        path = self.store / 'page.html'; path.write_text('<html><script></script></html>')
        def fail(_):
            raise OSError('viewer failed')
        with self.assertRaises(OSError):
            self.journal.receipt('plan', path, fail)
        self.assertEqual(self.journal.missing(editing=True), ['plan'])

    def test_artifacts_cannot_escape_or_replace_source(self):
        self.begin()
        with self.assertRaises(WorkflowError):
            self.journal.receipt('plan', self.repo / 'page.html', lambda _:None)
        link = self.store / 'escape.html'; link.symlink_to(self.repo / 'code.txt')
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
        self.begin()
        (self.repo / '.env').write_text('SECRET=not-read')
        with self.assertRaisesRegex(WorkflowError, 'never read'):
            self.deliver('plan')


if __name__ == '__main__':
    unittest.main()
