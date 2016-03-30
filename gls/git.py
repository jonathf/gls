import subprocess
import sys
import re
import os

def get_statuses(gpath, lpath):
    """
    Retrieve the git status on file in directory

    Args:
        gpath (str) : Absolute path to git root directory.
        lpath (str) : Relative path from git root to current directory.

    Returns:
        (dict) : Keys are filenames and values are raw git status codes.
    """

    os.chdir(gpath+lpath)

    cmd = "git status --ignored --porcelain -u ."

    if sys.version_info.major == 2:
        proc = subprocess.Popen(cmd, shell=True, stdout=-1)
        output = proc.communicate()[0]
    else:
        with subprocess.Popen(cmd, shell=True, stdout=-1) as proc:
            output = proc.stdout.read().decode("utf-8")

    regex = r"^(..) " + "."*len(lpath) + r"([^\n/>]*)$"
    statuses = {
        key[1] : key[0] for key in re.findall(regex, output, re.M)
    }
    regex = r"^(..) " + "."*len(lpath) + r"([^\n/>]*) -> (.+)$"
    statuses.update({
        key[1] : key[0]+key[2] for key in re.findall(regex, output, re.M)
    })

    return statuses


def remove_hidden(lfiles, statuses):
    """
Remove all hidden file instancecs that isn't tracked.

Args:
    lfiles (list) : Collection of filenames.
    statuses (dict) : Collection of two-letter file status codes.

Changes `lfiles` *IN PLACE*.
    """

    for lfile in lfiles[::-1]:

        if os.path.split(lfile)[-1][0] == "." \
                and statuses.get(lfile, "-") in ("!!", "??"):
            lfiles.remove(lfile)


def remove_untracked(lfiles, statuses):
    """
Remove all file instances that isn't tracked.

Args:
    lfiles (list) : Collection of filenames.
    statuses (dict) : Collection of two-letter file status codes.

Changes `lfiles` *IN PLACE*.
    """

    for lfile in lfiles[::-1]:

        if statuses.get(lfile, "-") == "??":
            lfiles.remove(lfile)


def remove_ignored(lfiles, statuses):
    """
Remove all file instances that are actively ignored.

Args:
    lfiles (list) : Collection of filenames.
    statuses (dict) : Collection of two-letter file status codes.

Changes `lfiles` *IN PLACE*.
    """
    for lfile in lfiles[::-1]:

        if statuses.get(lfile, "-") == "!!":
            lfiles.remove(lfile)



def add_renamed(lfiles, statuses):

    for original, status in statuses.items():

        if len(status) > 2:
            status, renamed = status[:2], status[2:]
            if renamed in lfiles:
                ind = lfiles.index(renamed)
                lfiles.insert(ind+1, original)
                statuses[original] = status
                statuses[renamed] = status.lower()
            else:
                ind = lfiles.index(original)
                lfiles.insert(ind, renamed)
                statuses[original] = status
                statuses[renamed] = "dd"


