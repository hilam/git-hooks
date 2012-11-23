"""Handling of annotated tag deletion."""

from git import commit_oneline
from updates.tags.ltag_deletion import LightweightTagDeletion


ATAG_DELETION_EMAIL_BODY_TEMPLATE = """\
The annotated tag '%(short_ref_name)s' was deleted.
It previously pointed to:

 %(commit_oneline)s"""


class AnnotatedTagDeletion(LightweightTagDeletion):
    """Update class for annotated tag deletion.

    REMARKS
        For tag deletion, there are only very small differences
        between lightweight tags and annotated tags.  Therefore,
        the implementation of some of the abstract methods is
        identical for both.  This explains why we inherit from
        LightweightTagDeletion.
    """
    def get_update_email_contents(self, email_info):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Deleted tag %s' % (email_info.project_name,
                                           self.short_ref_name)

        tag_info = {}
        tag_info['short_ref_name'] = self.short_ref_name
        tag_info['commit_oneline'] = commit_oneline(self.old_rev)
        body = ATAG_DELETION_EMAIL_BODY_TEMPLATE % tag_info

        return (subject, body)

