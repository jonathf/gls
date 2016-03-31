import sys
import os
import glob
from subprocess import Popen
import functools


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

