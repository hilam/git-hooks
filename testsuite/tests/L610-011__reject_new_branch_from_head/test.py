from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this situation, release-0.1-branch is a branch containing
        several commits attached to the HEAD of the master branch
        (master does not have any commit that release-0.1-branch does
        not have).
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a' `d'
remote: *** pre-commit check failed for commit: dcc477c258baf8cf59db378fcc344dc962ad9a29
remote: *** cvs_check: `repo' < `a' `b'
remote: *** ERROR: b: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/release-0.1-branch
To ../bare/repo.git
 ! [remote rejected] release-0.1-branch -> release-0.1-branch (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertTrue(p.status != 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Verify that the branch does not exist on the remote...

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())

        self.assertTrue(p.status != 0, p.image)


if __name__ == '__main__':
    runtests()
