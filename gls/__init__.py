"""
GLS -- Git list files

A ls-clone that weaves git-status information into output.
"""
import sys
import os
import re
from subprocess import Popen

from gls.configure import color, white, mapping
from gls.globbing import get_files, get_paths


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
        proc = Popen(cmd, shell=True, stdout=-1)
        output = proc.communicate()[0]
    else:
        with Popen(cmd, shell=True, stdout=-1) as proc:
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


def format_status(status):
    """
    Convert a raw git status to letter for the screen.  Mostly converting
    spaces to underscores.

    Args:
        status (str) : Raw two-letter git status code.

    Returns:
        (str) : Formatet two-letter git status code.

    """
    local, server = status
    if local == " ":
        local = "_"

    if server == " ":
        server = "_"

    if local == server == "_":
        local = server = " "

    return local + server



def word_color(status_local, status_server):
    """
    Select color for the status.

Args:
    status_local (str) : Single letter git status code.
    status_server (str) : Single letter git status code.

Returns:
    (str) : Bash color code respective to the color mapping rule.
    """

    for code in "UD?!MACRr":
        if code in status_local+status_server:
            return color[mapping[code]]

    return white


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


def add_color(lfiles, statuses):
    """
Get color prefixes to each file and folder.

Args:
    lfiles (list) : Collection of filenames.
    statuses (dict) : Collection of two-letter file status codes.

Returns:
    (list) : 
    """

    for i in range(len(lfiles)-1, -1, -1):

        file = lfiles[i]

        if os.path.isdir(file):
            prefix = color[mapping["dir"]] 
            postfix = "  "
        else:
            X, Y = format_status(statuses.get(lfiles[i], "  "))
            prefix = word_color(X, Y)
            if "r" in (X, Y):
                postfix = color["grey"] + "<-"
            else:
                postfix = "  "

        lfiles[i] = prefix + lfiles[i] + postfix + white


def add_renamed(lfiles, statuses):

    for original, status in statuses.items():

        if len(status) > 2:
            status, renamed = status[:2], status[2:]
            ind = lfiles.index(renamed)
            lfiles.insert(ind+1, original)

            statuses[original] = status
            statuses[renamed] = status.lower()


def main(args):

    gpath, lpath, files = get_files(args.FILE)

    statuses = get_statuses(gpath, lpath)

    if args.verbose:
        print("paths")
        print(gpath, lpath)
        print("before")
        print(files)
        print(statuses)


    if args.all:
        pass

    elif args.almost_all:
        remove_hidden(files, statuses)

    elif args.untracked:
        remove_hidden(files, statuses)
        remove_ignored(files, statuses)

    else:
        remove_hidden(files, statuses)
        remove_ignored(files, statuses)
        remove_untracked(files, statuses)

    add_renamed(files, statuses)

    lengths = [len(f) for f in files]
    add_color(files, statuses)

    if args.verbose:
        print("after")
        print(files)
        print(statuses)

    print(format_table(files, statuses, lengths, args.width))


def format_table(files, statuses, lengths, disp_width=None):
    "format table for output"

    if not disp_width:
        proc = Popen('tput cols', shell=1, stdout=-1)
        disp_width = int(proc.communicate()[0])

    max_name_width = max(lengths)
    n_cols = int(disp_width / (max_name_width+2))

    sizes = [2]*n_cols
    i = 0
    for length in lengths:
        sizes[i] = max(sizes[i], length)
        i += 1
        if i == n_cols:
            i = 0

    out = ""
    i = 0
    for length,name in zip(lengths, files):

        out += name + " "*(sizes[i]-length)
        i += 1
        if i == n_cols:
            out += "\n"
            i = 0

    if out and out[-1] == "\n":
        out = out[:-1]

    return out

