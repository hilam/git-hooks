"""A module to determine file attribute values at any commit.

This code could logically belong in git.py, but it is kept here instead,
because it makes some assumptions that are specific to AdaCore (Eg:
we take into account a default_attributes file in info/).
"""

import os
from os.path import dirname, isfile
from shutil import copy

from git import git, file_exists

# The name of the default attributes file in the bare repository.
# This file expected to be relative to the root of the bare repository.
DEFAULT_ATTRIBUTES_FILE='info/default_attributes'

def get_attribute(filename, attr_name):
    """Read GIT_DIR/info/attributes and return the file's attribute value.

    PARAMETERS:
        filename: See git_attribute function below.
        attr_name: See git_attribute function below.

    RETURN VALUE
        A string containing the attribute value.
    """
    attr_info = git.check_attr(attr_name, '--', filename)

    # Sanity check: attr_info should have the following format:
    # <FILENAME>: <ATTR_NAME>: <VALUE>.
    attr_info_prefix = '%s: %s: ' % (filename, attr_name)
    assert attr_info.startswith(attr_info_prefix)

    # Return the portion of the output that contains the attribute value.
    return attr_info[len(attr_info_prefix):]


def git_attribute(commit_rev, filename, attr_name):
    """Return filename's attribute value at commit_rev.

    PARAMETERS
        commit_rev: The commit to use in order to determine the
            attribute value.  This is important, because more recent
            commits may have changed the attribute value through
            updates of various .gitattributes files.
        filename: The name of the file for which the attribute is
            to be determined.  The file name should be relative to
            the root of the repository.
        attr_name: The name of the attribute.

    RETURN VALUE
        A string containing the attribute value.

    REMARKS
        The problem is not as easy as it looks.  If we were working
        from a full (non-bare) repository, the `git check-attr'
        command would give us our answer immediately.  But in bare
        repositories, the only file read is GIT_DIR/info/attributes.

        We solve the problem this way.  Starting from the directory
        where our file is located, find the first .gitattribute file
        that specifies an attribute value for our file.  If we read
        the gitattributes(5) man page correctly, that should yield
        the correct answer. Furthermore, if none of the .gitattributes
        file yielded a value for this attribute, then try one last
        time with GIT_DIR/info/default_attributes (if it exists).
    """
    path = filename
    attr_value = 'unspecified'

    keep_going = True
    while path:
        path = dirname(path)
        gitattributes_file = os.path.join(path, '.gitattributes')

        if file_exists(commit_rev, gitattributes_file):
            # Get the .gitattributes files in that directory, and save it
            # as GIT_DIR/info/attributes, and then get `git check-attr'
            # to read it for us.
            git.show('%s:%s' % (commit_rev, gitattributes_file),
                     _outfile='info/attributes')
            attr_value = get_attribute(filename, attr_name)

            # If this .gitattribute file provided us with an attribute
            # value, then we're done.
            if attr_value != 'unspecified':
                break

    # If none of the .gitattributes files in the project provided
    # an attribute value, then check the `info/default_attributes'
    # file.
    if attr_value == 'unspecified' and isfile(DEFAULT_ATTRIBUTES_FILE):
        copy(DEFAULT_ATTRIBUTES_FILE, 'info/attributes')
        attr_value = get_attribute(filename, attr_name)

    return attr_value
