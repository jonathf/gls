"""
Library for GLS
"""

import sys
import os
import pwd
import glob
import subprocess
import re
import time

import glslib.config
import glslib.format
import glslib.globbing


def filter_content(lfiles, statuses, args):
    """
Remove files from list that are supposed to be hidden. In addition, reformat
files related to renaming.

Args:
    lfiles (list) : A list containing a full paths retrieved after glob.
    statuses (dict) : A dictionary containtin all statuses.
    args (dict) : Argparse object.

Returns:
    (list) : List of files, where unwanted files are removed, and renames are
             fixed.

Note:
    Statuses are changed in place for renamed in git work tree.
    """

    ignored = True - args.all - args.ignored
    hidden = True - args.all
    untracked = args.untracked - args.all

    lfiles = lfiles[:]
    out = []

    while lfiles:
        lfile = lfiles.pop(0)

        status = statuses.get(lfile, "")

        if len(status) > 2:

            status, renamed = status[:2], status[2:]

            if renamed in lfiles:

                lfiles.remove(renamed)
                lfiles.insert(0, lfile)
                lfiles.insert(0, renamed)
                statuses[lfile] = status
                statuses[renamed] = status.lower()

            elif renamed in out:
                out.remove(renamed)
                lfiles.insert(0, lfile)
                lfiles.insert(0, renamed)
                statuses[lfile] = status
                statuses[renamed] = status.lower()

            else:
                lfiles.insert(0, lfile)
                lfiles.insert(0, renamed)
                statuses[lfile] = status
                statuses[renamed] = "dd"

        else:
            hidden_ = status in ("!!", "??", "") and hidden and\
                os.path.split(lfile)[-1][0] == "."
            untracked_ = status == "??" and untracked
            ignored_ = status == "!!" and ignored

            if not hidden_ and not untracked_ and not ignored_:
                out.append(lfile)

    return out


def main(args):
    """
    The main module.
    """

    userinput = args.FILE
    if not userinput:
        userinput = ["."]

    git_statuses = glslib.globbing.get_git_status(userinput)
    lfiles = glslib.globbing.expand_glob(userinput, git_statuses)
    lfiles = filter_content(lfiles, git_statuses, args)

    folders = [os.path.dirname(j) + os.sep for j in lfiles]

    curdir = os.path.abspath(".")
    titles = []

    curdir_included = False

    groups = []
    if curdir in folders:
        curdir_included = True

        group = glslib.format.format_group(curdir, folders, lfiles,
                                           git_statuses, args.human_readable,
                                           args.long, args.width)
        groups.append(group)

    while folders:
        group = []
        path = folders[0]

        color = glslib.config.mapping["dir"]
        titles.append(
            glslib.config.color[color] + os.path.relpath(path) + "/:")

        group = glslib.format.format_group(path, folders, lfiles, git_statuses,
                                           args.human_readable,
                                           args.long,
                                           args.width)
        groups.append(group)

    out = ""
    if len(groups) == 1 or curdir_included:
        out = groups.pop(0)

    for group, title in zip(groups, titles):
        if out:
            out += "\n\n"

        out += title + "\n" + group

    out += glslib.config.color["white"]
    return out
