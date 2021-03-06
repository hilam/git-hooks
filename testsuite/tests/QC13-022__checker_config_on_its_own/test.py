from support import *


class TestRun(TestCase):
    def test_push_commits_on_master(self):
        cd('%s/repo' % TEST_DIR)

        # Push the commit adding the style-checker-config-file option
        # to the refs/meta/config branch.
        p = Run('git push origin meta-config:refs/meta/config'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo(refs/meta/config)] Add style-checker-config-file option
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: a6817570d8c09b1f07446e75eced8a5c337c8b8a
remote: X-Git-Newrev: b2657ce03d358899ce2c779ecf68ac7e8e670dd0
remote:
remote: commit b2657ce03d358899ce2c779ecf68ac7e8e670dd0
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 9 07:29:59 2017 +0100
remote:
remote:     Add style-checker-config-file option
remote:
remote: Diff:
remote: ---
remote:  project.config | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/project.config b/project.config
remote: index 93a508c..790a7b5 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,3 +1,4 @@
remote:  [hooks]
remote:          from-domain = adacore.com
remote:          mailinglist = git-hooks-ci@example.com
remote: +        style-checker-config-file = style.yaml
To ../bare/repo.git
   a681757..b2657ce  meta-config -> refs/meta/config
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a commit to the repository to a branch where
        # the style checker's config file does not exist yet...

        p = Run('git push origin step-1/checker_config_missing:master'.split())
        expected_out = """\
remote: *** Cannot file style_checker config file: `style.yaml'.
remote: ***
remote: *** Your repository is configured to provide a configuration file to
remote: *** the style_checker; however, I cannot find this configuration file
remote: *** (style.yaml) in commit 555923ece17519f0afeed78625afc6ab7e64e592.
remote: ***
remote: *** Perhaps you haven't added this configuration file to this branch
remote: *** yet?
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] step-1/checker_config_missing -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Once the checkin above did not work, push a commit which
        # adds the missing config file (on its own)

        p = Run('git push origin step-2/add_checker_config_file:master'.split())
        expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Add style.yaml (auxillary config file for the style_checker)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: b3a13b32c1b76333cdf5135381a20b98c41f9897
remote: X-Git-Newrev: c84b233ceaf4009eb923d25fbbb632ddc1daa4aa
remote:
remote: commit c84b233ceaf4009eb923d25fbbb632ddc1daa4aa
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 13 16:09:34 2017 +0400
remote:
remote:     Add style.yaml (auxillary config file for the style_checker)
remote:
remote: Diff:
remote: ---
remote:  style.yaml | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/style.yaml b/style.yaml
remote: new file mode 100644
remote: index 0000000..b3fcae2
remote: --- /dev/null
remote: +++ b/style.yaml
remote: @@ -0,0 +1 @@
remote: +# A YaML file (with nothing in it)
To ../bare/repo.git
   b3a13b3..c84b233  step-2/add_checker_config_file -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Once the config file is in, we should now be able to push
        # our commit, this time.

        p = Run('git push origin step-3/try_initial_commit_again:master'
                .split())
        expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `b.adb'
remote: *** # A YaML file (with nothing in it)
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] b.adb: Print message when done.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: c84b233ceaf4009eb923d25fbbb632ddc1daa4aa
remote: X-Git-Newrev: bf95cd2158bada71f60ae9f742370452b46c4582
remote:
remote: commit bf95cd2158bada71f60ae9f742370452b46c4582
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 9 07:23:40 2017 +0100
remote:
remote:     b.adb: Print message when done.
remote:
remote: Diff:
remote: ---
remote:  b.adb | 2 ++
remote:  1 file changed, 2 insertions(+)
remote:
remote: diff --git a/b.adb b/b.adb
remote: index 20a8315..df29668 100644
remote: --- a/b.adb
remote: +++ b/b.adb
remote: @@ -1,5 +1,7 @@
remote:  with A;
remote: +with GNAT.IO; use GNAT.IO;
remote:  procedure B is
remote:  begin
remote:     A.Gloval_Bar := @ + 1;
remote: +   Put_Line ("Done!");
remote:  end B;
To ../bare/repo.git
   c84b233..bf95cd2  step-3/try_initial_commit_again -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Simulate a change where we only change the config file...
        # We expect that config file to be effective immediately,
        # so we verify that the contents of that file as passed
        # to our style_checker (cvs_check in our testsuite) shows
        # the updated contents.

        p = Run('git push origin step-4/modify_checker_config_only:master'
                .split())
        expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: *** hello: world
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] style.yaml: Set "hello" to "world".
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: bf95cd2158bada71f60ae9f742370452b46c4582
remote: X-Git-Newrev: 2e2c5c515364d94be300928ffc9507834843acdf
remote:
remote: commit 2e2c5c515364d94be300928ffc9507834843acdf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 13 16:17:00 2017 +0400
remote:
remote:     style.yaml: Set "hello" to "world".
remote:
remote: Diff:
remote: ---
remote:  style.yaml | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/style.yaml b/style.yaml
remote: index b3fcae2..817407e 100644
remote: --- a/style.yaml
remote: +++ b/style.yaml
remote: @@ -1 +1,2 @@
remote:  # A YaML file (with nothing in it)
remote: +hello: world
To ../bare/repo.git
   bf95cd2..2e2c5c5  step-4/modify_checker_config_only -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # And finally, simulate a commit which changes both the config
        # file and other files.
        #
        # Same as above, we expect the update config file to be effective
        # immediately, so we verify that the contents of that file as
        # passed to our style_checker (cvs_check in our testsuite) shows
        # the updated contents.

        p = Run('git push origin step-5/modify_code_and_checker_config:master'
                .split())
        expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `a.ads' `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: *** hello: world
remote: *** something: else
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] set Global_Var's initial value to 20 and adapt style.yaml
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 2e2c5c515364d94be300928ffc9507834843acdf
remote: X-Git-Newrev: bdd1bbb4ec3cc746bf2c26d8d204ec6cd6d86553
remote:
remote: commit bdd1bbb4ec3cc746bf2c26d8d204ec6cd6d86553
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 13 16:17:54 2017 +0400
remote:
remote:     set Global_Var's initial value to 20 and adapt style.yaml
remote:
remote: Diff:
remote: ---
remote:  a.ads      | 2 +-
remote:  style.yaml | 1 +
remote:  2 files changed, 2 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a.ads b/a.ads
remote: index 2153543..c63a723 100644
remote: --- a/a.ads
remote: +++ b/a.ads
remote: @@ -1,3 +1,3 @@
remote:  package A is
remote: -   Gloval_Bar : Integer := 15;
remote: +   Gloval_Bar : Integer := 20;
remote:  end A;
remote: diff --git a/style.yaml b/style.yaml
remote: index 817407e..1097710 100644
remote: --- a/style.yaml
remote: +++ b/style.yaml
remote: @@ -1,2 +1,3 @@
remote:  # A YaML file (with nothing in it)
remote:  hello: world
remote: +something: else
To ../bare/repo.git
   2e2c5c5..bdd1bbb  step-5/modify_code_and_checker_config -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
