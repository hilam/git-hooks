from support import *
from subprocess import check_output, check_call

class TestRun(TestCase):
    def __bare_repo_fixup(self):
        """Fix the bare repository to implement legacy hooks configuration.

        Reproduce the (legacy) situation where the project.config file
        in refs/meta/config does not exist, and where the repository's
        hooks configuration is stored inside the repository's config
        file.
        """
        # First, extract the configuration, available at the standard
        # location.
        cfg_txt = check_output(
            'git show refs/meta/config:project.config'.split(),
            cwd='%s/bare/repo.git' % TEST_DIR)
        with open('%s/bare/repo.git/config' % TEST_DIR, 'a') as f:
            f.write(cfg_txt)
        check_call('git update-ref -d refs/meta/config'.split(),
                   cwd='%s/bare/repo.git' % TEST_DIR)

    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        self.__bare_repo_fixup()

        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** -----------------------------------------------------------------
remote: *** Unable to find file project.config from branch refs/meta/config
remote: *** Using your repository's config file instead.
remote: ***
remote: *** This is not a fatal issue, but please contact your repository's
remote: *** administrator to set your project.config file up.
remote: *** -----------------------------------------------------------------
remote: *** cvs_check: `trunk/repo/a'
remote: *** -----------------------------------------------------------------
remote: *** Unable to find file project.config from branch refs/meta/config
remote: *** Using your repository's config file instead.
remote: ***
remote: *** This is not a fatal issue, but please contact your repository's
remote: *** administrator to set your project.config file up.
remote: *** -----------------------------------------------------------------
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: commit a60540361d47901d3fe254271779f380d94645f7
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()