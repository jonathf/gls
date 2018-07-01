"""Identify system and git statuses for given set of user given paths."""

import os
import sys
import subprocess
import glob
import re
import pwd
import grp
import time


def git_command(cmd, folder):
    """
    Perform a git command and return stdout from the operation.

    Args:
        cmd (str) : Command to be performed.
        folder (str) : Folder where operation should be performed.

    Returns:
        (str) : The output from running the command.
    """
    curfolder = os.path.abspath(".")
    os.chdir(folder)

    if sys.version_info.major == 2:
        proc = subprocess.Popen(cmd, shell=True, stdout=-1, stderr=-1)
        results = proc.communicate()[0]
    else:
        with subprocess.Popen(cmd, shell=True, stdout=-1, stderr=-1) as proc:
            results = proc.stdout.read().decode("utf-8")
    os.chdir(curfolder)

    if results[-1:] == "\n":
        results = results[:-1]

    return results


def sorting_key(key):
    """Key for which files and folders are sorted."""
    if os.path.basename(key)[:1] == ".":
        return os.path.dirname(key).lower() + os.sep +\
            os.path.basename(key)[1:].lower()
    return key.lower()


def expand_glob(lpaths, git_statuses):
    """
    Expand a list of filenames/dirnames/globs.

    Args:
        lpaths (list) : Unaltered user input with globs.
        gpaths (list) : List of full paths from git working tree.

    Returns:
        (list) : list of expanded paths
    """
    gpaths = sorted(set(git_statuses.values()), key=sorting_key)
    gitpathstring = "\n".join(gpaths)

    out = []
    lpaths = lpaths[:]

    while lpaths:
        lpath = lpaths.pop(0)

        if os.path.isdir(lpath):
            lpath = os.path.abspath(lpath) + os.sep

            lpath_sys = glob.glob(lpath + "*") + glob.glob(lpath + ".*")

            regex = "^" + re.escape(lpath) + "[^/]+$"
            lpath_git = re.findall(regex, gitpathstring, re.M)

            out.extend(sorted(set(lpath_sys + lpath_git),
                              key=sorting_key))

        elif os.path.isfile(lpath):
            lpath = os.path.abspath(lpath)
            out.append(lpath)

        elif "*" in lpath:

            regex = re.escape(lpath).replace(r"\*", r"[^/]*")
            regex = "^" + regex + "$"
            out.extend(sorted(re.findall(regex, gitpathstring, re.M),
                              key=sorting_key))
            lpaths = sorted(glob.glob(lpath),
                            key=sorting_key) + lpaths

        else:
            print(lpath, "not recognised!")

    seen = set()
    out = [x for x in out if not (x in seen or seen.add(x))]
    if "" in out:
        out.remove("")

    folders = [os.path.dirname(j) + os.sep for j in out]
    cmd = "git ls-tree --name-status HEAD"

    for folder in folders:
        paths = git_command(cmd, folder)
        for line in paths.split("\n"):
            if line and folder+line not in git_statuses:
                git_statuses[folder + line] = "TT"

    return out


def get_git_status(lfiles):
    """
    Get git status for a given list of files.

    Args:
        lfiles (list) : List of unmodified user input.

    Returns:
        (dict) : Keys are full paths, and values are git status codes.
    """
    globs = []
    lfiles = lfiles[:]
    while lfiles:

        lfile = lfiles.pop(0)

        if os.path.isdir(lfile):

            lfile = os.path.abspath(lfile) + os.sep
            lfile_glob = glob.glob(lfile + "*")
            globs.extend(lfile_glob)

        elif os.path.isfile(lfile):

            globs.append(os.path.abspath(lfile))

        elif "*" in lfile:

            lfiles = glob.glob(lfile) + lfiles

    folders = [os.path.dirname(lfile) for lfile in globs]

    cmd = "git rev-parse --git-dir"
    git_paths = {
        os.path.dirname(
            os.path.abspath(
                git_command(cmd, folder)
            )
        ) + os.sep
        for folder in set(folders)
    }

    if "" in git_paths:
        git_paths.remove("")

    out = {}
    cmd = "git status --ignored --porcelain -u ."
    regex1 = re.compile(r"^(..) ([^ ]*)$", re.M)
    regex2 = re.compile(r"^(..) ([^ ]*) -> (.+)$", re.M)

    for git_path in git_paths:

        statuses = git_command(cmd, git_path)

        out.update({
            git_path + key[1]: key[0]
            for key in re.findall(regex1, statuses)
        })
        out.update({
            git_path + key[1]: key[0] + git_path + key[2]
            for key in re.findall(regex2, statuses)
        })

    return out


def format_filesize(size, human=False):
    """Format file size for output."""
    if human:
        if size < 1024.0:
            return "%d" % size

        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
            if size < 1024.0:
                return "%3.1f%s" % (size, unit)
            size /= 1024.0

        return ">Y"

    return str(size)


def format_time(mtime):
    """Format time for output."""
    six_months_ago = time.time() - 180*24*60

    if mtime > six_months_ago:
        return time.strftime("%b;%d %H:%I", time.localtime(mtime)).split(";")

    return time.strftime("%b;%d  %Y", time.localtime(mtime)).split(";")


def get_sys_status(lfiles, human=False):
    """
    Get system information about files.

    Args:
        lfiles (list) : list of full paths
        human (bool) : Human readable file sizes

    Returns:
        (list) : Set of tuples with system information on format
                 `(mode, owner, group, size, mtime1, mtime2)`
    """
    out = []
    for lfile in lfiles:

        if os.path.isfile(lfile):
            if os.path.islink(lfile):
                pre = "l"
            else:
                pre = "-"

        elif os.path.isdir(lfile):
            pre = "d"

        else:
            out.append(("", "", "", "", "", ""))
            continue

        mode = bin(os.stat(lfile).st_mode)[-9:]
        mode = pre + "".join([m == "1" and M or "-"
                              for m, M in zip(mode, "rwxrwxrwx")])
        stat = os.stat(lfile)
        owner = pwd.getpwuid(stat.st_uid).pw_name
        group = grp.getgrgid(stat.st_gid).gr_name 

        size = format_filesize(stat.st_size, human)

        mtime1, mtime2 = format_time(stat.st_atime)

        out.append((mode, owner, group, size, mtime1, mtime2))

    return out
