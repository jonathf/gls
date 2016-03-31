import sys
import os
import glob
from subprocess import Popen
import functools
from collections import OrderedDict as odict

def get_repo_paths(files, recursive=False):
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
    curdir = os.path.abspath(os.curdir)

    if not files:
        files = ["."]

    repos = []

    if len(files) == 1 and os.path.isdir(files[0]):

        if recursive:
            for root, folders, fs in os.walk(files[0]):
                for folder in folders:
                    repos.extend(get_repo_paths(dir))

        else:

            os.chdir(os.path.dirname(lfile))
            cmd = "git rev-parse --git-dir"

            if sys.version_info.major == 2:
                proc = Popen(cmd, shell=True, stdout=-1)
                gpath = proc.communicate()[0]
            else:
                with Popen(cmd, shell=True, stdout=-1) as proc:
                    gpath = proc.stdout.read().decode("utf-8")

            if gpath:
                repos.append(odict([gpath, [lfile + os.sep + "*"]})
            else:
                repos.append(odict([("", [lfile + os.sep + "*")]]})

    else:

        repo.append({})

        for lfile in files:

            if os.path.isdir(lfile) and lfile[-1] != os.sep:
                lfile = lfile + os.sep

            head, tail = os.path.split(lfile)

            if "*" in head:
                raise ValueError("Wildcard in path not supported")

            if not head:
                head = curdir
            head = os.path.abspath(head)
            


            lfile = os.path.abspath(lfile)

            if os.path.isdir(lfile):
                repos.extend(get_repo_paths(lfile + os.sep + "*"))

            os.chdir(os.path.dirname(lfile))
            cmd = "git rev-parse --git-dir"

            if sys.version_info.major == 2:
                proc = Popen(cmd, shell=True, stdout=-1)
                gpath = proc.communicate()[0]
            else:
                with Popen(cmd, shell=True, stdout=-1) as proc:
                    gpath = proc.stdout.read().decode("utf-8")

            if not gpath:
                repos[""] = lfile
                continue

            gpath = os.path.abspath(gpath)[:-5]
            lpath = path[len(gpath):]
            if lpath:
                lpath = lpath + "/"

            repos[gpath] = lpath

        return repos


# obsolete
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

    if not directory:
        directory = "."
    path = os.path.abspath(directory)
    os.chdir(path)

    cmd = "git rev-parse --git-dir"
    if sys.version_info.major == 2:
        proc = Popen(cmd, shell=True, stdout=-1)
        gpath = proc.communicate()[0]
    else:
        with Popen(cmd, shell=True, stdout=-1) as proc:
            gpath = proc.stdout.read().decode("utf-8")
    gpath = os.path.abspath(gpath)[:-5]
    lpath = path[len(gpath):]
    if lpath:
        lpath = lpath + "/"

    assert os.path.isdir(gpath)
    assert os.path.isdir(gpath+lpath)

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
    gpath, lpath = get_paths(path)

    files = glob.glob(gpath+lpath+"/*")
    files += glob.glob(gpath+lpath+"/.*")
    files = [f[len(gpath+lpath):] for f in files]

    if ".git" in files:
        del files[files.index(".git")]

    def _cmp(lhs, rhs):
        while lhs and lhs[0] == ".":
            lhs = lhs[1:]
        while rhs and rhs[0] == ".":
            rhs = rhs[1:]

        lhs = lhs.lower()
        rhs = rhs.lower()

        return 1*(lhs == rhs) + 1*(lhs > rhs) - 1

    if sys.version_info.major == 2:
        files.sort(cmp=_cmp)
    else:
        files = sorted(files, key=functools.cmp_to_key(_cmp))

    return gpath, lpath, files

