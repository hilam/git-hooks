"""Implements git's post-receive hook.

The arguments for this hook are passed via stdin: For each reference
that is updated, stdin contains one line with 3 space-separated
tokens: the old SHA1, the new SHA1, and the reference name (Eg:
refs/heads/master).
"""
from argparse import ArgumentParser
from collections import OrderedDict
from email.mime.text import MIMEText
from email.utils import parseaddr, getaddresses
import os
import re
import smtplib
import sys

from config import git_config
from git import (get_module_name, is_null_rev, get_object_type,
                 commit_oneline)
from utils import debug, warn, get_user_name, get_user_full_name


class PostReceiveError(Exception):
    """A fatal issue during the post-receive hook.
    """


# All commit emails should be sent to the following email address
# for filing/archiving purposes...
FILER_EMAIL='file-ci@gnat.com'

def send_email(e_msg):
    """Send the given e_msg.

    PARAMETERS
        e_msg: An email.message.Message object.
    """
    email_from = parseaddr(e_msg.get('From'))
    email_recipients = [addr[1] for addr
                        in getaddresses(e_msg.get_all('To', [])
                                        + e_msg.get_all('Cc', [])
                                        + e_msg.get_all('Bcc', []))]

    if 'GIT_HOOKS_TESTSUITE_MODE' in os.environ:
        # Use debug level 0 to make sure that the trace is always
        # printed.
        debug(e_msg.as_string(), level=0)
    else: # pragma: no cover (do not want to send real emails during testing)
        s = smtplib.SMTP('localhost')
        s.sendmail(email_from, email_recipients, e_msg.as_string())
        s.quit()


class AbstractRefChange(object):
    """Abstract class dealing with reference change.

    The references in question can be any reference, including tags,
    or branches.  The change can be the creation of that reference,
    the deletion of that reference, or the update of that reference.

    ATTRIBUTES
        ref_name
        old_rev
        new_rev
        short_ref_name
        project_name

        email_from
        email_to
        email_subject

    ABSTRACT ATTRIBUTES
        email_subject:
        email_body:
    """
    def __init__(self, ref_name, old_rev, new_rev,
                 project_name, email_from, email_to):
        self.old_rev = old_rev
        self.new_rev = new_rev
        self.ref_name = ref_name

        m = re.match(r"refs/[^/]*/(.*)", ref_name)
        self.short_ref_name = m.group(1) if m else ref_name

        self.project_name = project_name

        self.email_from = email_from
        self.email_to = email_to
        self.email_subject = None # To be created by child class.
        self.email_body = None # To be created by child class.

    def send_email(self):
        # Chances are very low that the size of this email would be
        # greater than the maximum email size.  So do not truncate
        # the email body.
        e_msg = MIMEText(self.email_body)

        # Create the e_msg header.
        e_msg['From'] = self.email_from
        e_msg['To'] = self.email_to
        e_msg['Bcc'] = FILER_EMAIL
        e_msg['Subject'] = self.email_subject
        e_msg['X-ACT-checkin'] = self.project_name
        e_msg['X-Git-Refname'] = self.ref_name
        e_msg['X-Git-Oldrev'] = self.old_rev
        e_msg['X-Git-Newrev'] = self.new_rev

        send_email(e_msg)


class LightweightTagCreation(AbstractRefChange):
    """An unannotated tag creation...
    """
    def __init__(self, ref_name, old_rev, new_rev,
                 project_name, email_from, email_to):
        AbstractRefChange.__init__(self, ref_name, old_rev, new_rev,
                                   project_name, email_from, email_to)

        self.email_subject = '[%s] Created tag %s' % (self.project_name,
                                                      self.short_ref_name)
        self.email_body = ("""\
The lightweight tag '%(short_ref_name)s' was created pointing to:

 %(commit_oneline)s"""
                       % {'short_ref_name' : self.short_ref_name,
                          'commit_oneline' : commit_oneline(self.new_rev),
                         })


# The different types of reference updates:
#    - CREATE: The reference is new and has just been created;
#    - DELETE: The reference has just been deleted;
#    - UPDATE: The reference already existed before and its value
#              has just been udpated.
# These constants act as poor-man's enumerations.
(CREATE, DELETE, UPDATE) = range(3)

# A dictionary that maps the type of update to the associated
# concrete RefChange class.
#
# This dictionary is indexed by a tuple with the following entries:
#    [0] The reference name prefix: The name of the reference being
#        updated must start with this prefix;
#    [1] The type of update (one of the CREATE, DELETE, etc, constants
#        above);
#    [2] The object type (usually 'tag' or 'commit').

REF_CHANGE_MAP = {
    ('refs/tags/', CREATE, 'commit') : LightweightTagCreation,
}


def post_receive_one(ref_name, old_rev, new_rev, project_name,
                     email_from, email_to):
    debug('post_receive_one(ref_name=%s\n'
          '                        old_rev=%s\n'
          '                        new_rev=%s)'
          % (old_rev, new_rev, ref_name))

    # Check the hooks.noemail configuration parameter.  If it exists,
    # it is a comma-separated list of names of ref names for which commits
    # should not trigger an update email.
    no_emails = git_config("hooks.noemails")
    if no_emails and ref_name in no_emails.split(","):
        print "---------------------------------------------------------------"
        print "-- The hooks.noemails config parameter contains `%s'." % ref_name
        print "-- Commit emails will therefore not be sent."
        print "---------------------------------------------------------------"

    # Note: The old version of these scripts were canonicalizing
    # old_rev and new_rev using "git rev-parse".  But, not knowing
    # whether this is really necessary or not, or under which
    # condition it would be necessary, we refrain from doing it
    # here.

    # At least one of the references must be non-null...
    assert not (is_null_rev(old_rev) and is_null_rev(new_rev))

    if is_null_rev(old_rev):
        change_type = CREATE
        object_type = get_object_type(new_rev)
    elif is_null_rev(new_rev):
        change_type = DELETE
        object_type = get_object_type(old_rev)
    else:
        change_type = UPDATE
        object_type = get_object_type(new_rev)

    ref_change_klass = None
    for key in REF_CHANGE_MAP:
        (map_ref_prefix, map_change_type, map_object_type) = key
        if (change_type == map_change_type
            and object_type == map_object_type
            and ref_name.startswith(map_ref_prefix)):
            ref_change_klass = REF_CHANGE_MAP[key]
            break

    if ref_change_klass is None:
        warn("post-receive: Unsupported reference update: %s,%s (ignored)."
             % (ref_name, object_type))

    change = ref_change_klass(ref_name, old_rev, new_rev, project_name,
                              email_from, email_to)
    change.send_email()


def post_receive(refs):
    """Implement the post-receive hook for all given refs.

    PARAMETERS
        refs: An OrderedDict, indexed by the name of the ref being updated,
            and containing 2-elements tuple.  This tuple contains the
            previous revision, and the new revision of the reference.
    """
    from_domain = git_config('hooks.fromdomain')
    if not from_domain:
        raise PostReceiveError(
            'Error: post-receive: hooks.fromdomain config variable not set.',
            'Cannot send email notifications.')

    email_to = git_config('hooks.mailinglist')
    if not email_to:
        # We should really refuse updates if this config variable is
        # not set.  But since this is too late to refuse the update,
        # at least try to file the commits (after having warned the user).
        warn('Warning: hooks.mailinglist config variable not set.\n'
             'sending emails to %s only' % FILER_EMAIL)
        email_to=FILER_EMAIL

    project_name = get_module_name()
    email_from = '%s <%s@%s>' % (get_user_full_name (),
                                 get_user_name (),
                                 from_domain)

    for ref_name in refs.keys():
        (old_rev, new_rev) = refs[ref_name]
        post_receive_one(ref_name, old_rev, new_rev, project_name,
                         email_from, email_to)


def parse_command_line(args):
    """Return a namespace built after parsing the command line.
    """
    # The command-line interface is very simple, so we could possibly
    # handle it by hand.  But it's nice to have features such as
    # -h/--help switches which come for free if we use argparse.
    #
    # We use ArgumentParser, which means that we are requiring
    # Python version 2.7 or later, because it handles mandatory
    # command-line arguments for us as well.
    ap = ArgumentParser(description='Git "update" hook.')
    ap.add_argument('old_rev',
                    help='the SHA1 before update')
    ap.add_argument('new_rev',
                    help='the new SHA1, if the update is accepted')
    ap.add_argument('ref_name',
                    help='the name of the reference being updated')

    return ap.parse_args(args)


if __name__ == '__main__':
    refs_data = OrderedDict()
    for line in sys.stdin:
        stdin_argv = line.strip().split()
        args = parse_command_line(stdin_argv)
        refs_data[args.ref_name] = (args.old_rev, args.new_rev)
    try:
        post_receive(refs_data)
    except PostReceiveError, E:
        warn(*E)
