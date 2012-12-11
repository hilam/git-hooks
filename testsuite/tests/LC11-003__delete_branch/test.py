from support import *

class TestRun(TestCase):
    def test_delete_branch(self):
        """Try deleting a branch on the remote.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :old-branch'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Deleted branch old-branch
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/heads/old-branch
remote: X-Git-Oldrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'old-branch' was deleted.
remote: It previously pointed to:
remote:
remote:  cc8d2c2... Modify `c', delete `b'.
To ../bare/repo.git
 - [deleted]         old-branch
"""
        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()