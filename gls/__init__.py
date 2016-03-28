"""
GLS -- Git list files

A ls-clone that weaves git-status information into output.
"""
import sys
from subprocess import Popen
import glob
import os
import functools
import re

from gls.configure import color, white, mapping


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
        statuses = proc.communicate()[0]
    else:
        with Popen(cmd, shell=True, stdout=-1) as proc:
            statuses = proc.stdout.read().decode("utf-8")

    regex = r"^(..) " + "."*len(gpath) + r"([^\n/]*)$"
    statuses = {
        key[1] : key[0] for key in re.findall(regex, statuses, re.M)
    }

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



def get_paths(directory):
    """
    Get absolute path to root git directory and local path from root directory
    to directory of interest.

    Args:
        directory (str) : Path (relative or absolute) to folder of interest.

    Returns:
        (gpath, lpath) : 
            gpath (str) : Absolute path to git root directory.
            lpath (str) : Relative path from git root to folder of interest.
    """

    path = os.path.abspath(directory)
    os.chdir(path)

    cmd = "git rev-parse --git-dir"
    if sys.version_info.major == 2:
        proc = Popen(cmd, shell=True, stdout=-1)
        gpath = proc.communicate()[0]
    else:
        with Popen(cmd, shell=True, stdout=-1) as proc:
            gpath = proc.stdout.read().decode("utf-8")
    gpath = gpath[:-7]
    lpath = path[len(gpath):]

    return gpath, lpath


def get_files(path):
    """
    Get all files (hidden and visible) and strip paths relative to folder of
    interest. Omits `.git` folder.

    Args:
        path (str) : Absolute path to direcgtory of interest.

    Returns:
        (list) : List of file and folder names in directory.
    """

    files = glob.glob(path+"/*")
    files += glob.glob(path+"/.*")
    files = [f[len(path)+1:] for f in files]

    if ".git" in files:
        del files[files.index(".git")]

    def _cmp(lhs, rhs):
        while lhs and lhs[0] == ".":
            lhs = lhs[1:]
        while rhs and rhs[0] == ".":
            rhs = rhs[1:]

        return 1*(lhs == rhs) + 1*(lhs < rhs) - 1

    if sys.version_info.major == 2:
        files.sort(cmp=_cmp)
    else:
        files = sorted(files, key=functools.cmp_to_key(_cmp))

    return files


def word_color(status_local, status_server):
    """
    Select color for the status.

Args:
    status_local (str) : Single letter git status code.
    status_server (str) : Single letter git status code.

Returns:
    (str) : Bash color code respective to the color mapping rule.
    """

    for code in "UD?!MACR":
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


def get_prefixes(lfiles, statuses):
    """
Get color prefixes to each file and folder.

Args:
    lfiles (list) : Collection of filenames.
    statuses (dict) : Collection of two-letter file status codes.

Returns:
    (list) : 
    """

    prefix = [white + "  "]*len(files)
    for i in range(len(files)-1, -1, -1):

        file = files[i]

        if os.path.isdir(file):
            prefix[i] = color[mapping["dir"]] + "  "
            continue

        X, Y = format_status(statuses.pop(files[i], "  "))

        cX = color[mapping[X]]
        cY = color[mapping[Y]]
        cZ = word_color(X, Y)
        prefix[i] = cX + X + cY + Y + cZ

    return prefix


def main(args):

    gpath, lpath = get_paths(args.DIR)

    files = get_files(gpath + lpath)
    statuses = get_statuses(gpath, lpath)

    if args.verbose:
        print("before")
        print(files)

    if args.verbose:
        print("statuses")
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

    lengths = [len(f) for f in files]
    prefixes = get_prefixes(files, statuses)

    if args.verbose:
        print("between")
        print(files)

    for file, status in statuses.items():

        X, Y = format_status(status)

        if file[0] == "." and X in "!?"\
                and not args.all:
            if file in files:
                index = files.index(file)
                del files[index]
                del prefix[index]
                del lengths[index]
            continue
        elif args.almost_all:
            pass
        elif not args.ignored and X == "!":
            if file in files:
                index = files.index(file)
                del files[index]
                del prefix[index]
                del lengths[index]
            continue
        elif not args.untracked and X == "?":
            if file in files:
                index = files.index(file)
                del files[index]
                del prefix[index]
                del lengths[index]
            continue

        cX = color[mapping[X]]
        cY = color[mapping[Y]]
        cZ = word_color(X, Y)
        prefix.append(cX + X + cY + Y + cZ)
        lengths.append(len(file))
        files.append(file)

    if args.verbose:
        print("after")
        print(files)

    for i in range(len(files)-1, -1, -1):
        if " -> " in files[i]:
            f1, f2 = files[i].split(" -> ")
            index = files.index(f2)
            files[index] = files[index] + color["grey"] + "<-" + f1
            lengths[index] += lengths[i] + 2

            del files[i]
            del prefix[i]
            del lengths[i]

    if args.width:
        width = args.width
    else:
        proc = Popen('tput cols', shell=1, stdout=-1)
        width = int(proc.communicate()[0])

    if args.verbose:
        print("width", width)

    print(format_table(files, prefix, lengths, width))


def format_table(files, prefix, lengths, disp_width):
    "format table for output"

    max_name_width = max(lengths)
    n_cols = int(disp_width / (max_name_width+2))

    sizes = [2]*n_cols
    i = 0
    while lengths:
        length = lengths.pop(0)
        sizes[i] = sizes[i] < length and length or sizes[i]
        i += 1
        if i == n_cols:
            i = 0

    out = ""
    i = 0
    while files:
        name = files.pop(0)
        pre = prefix.pop(0)
        out += pre + name.ljust(sizes[i])+" "
        i += 1
        if i == n_cols:
            out += "\n"
            i = 0

    return out + color["white"]

