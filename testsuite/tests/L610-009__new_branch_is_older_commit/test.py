from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this testcase, the release-0.1-branch points to a commit
        that's one of the older commits in the "master" branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'release-0.1-branch'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote:
remote: The branch 'release-0.1-branch' was created pointing to:
remote:
remote:  4a325b3... 1 modified file, 1 new file.
To ../bare/repo.git
 * [new branch]      release-0.1-branch -> release-0.1-branch
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())
        expected_out = """\
4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
