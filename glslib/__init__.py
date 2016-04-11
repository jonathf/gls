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


def git_command(cmd, folder):
    """
Move to a directory, perform a git command and return stdout from the
operation.

Args:
    cmd (str) : Command to be performed.
    folder (str) : Valid folder on system.

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
    if os.path.basename(key)[:1] == ".":
        return os.path.dirname(key).lower() + os.sep +\
            os.path.basename(key)[1:].lower()
    return key.lower()


def format_files(lfiles, statuses):
    """
Format files to include color prefixes to each file and folder.

Args:
    lfiles (list) : Collection of full path filenames.
    statuses (dict) : Collection of two-letter file status codes.

Returns:
    (list) : The same filenames, but with color coding, two space postfix (or
             arrow if renaming).
    """

    out = []
    out_names = []
    lfiles = lfiles[:]
    next_exec = False

    while lfiles:

        lfile = lfiles.pop(0)

        if os.path.isdir(lfile):
            color = glslib.config.mapping["dir"]
            prefix = glslib.config.color[color]

            if os.path.islink(lfile):
                postfix = glslib.config.color["cyan"] + "^ "
            else:
                postfix = "  "

        else:
            code = statuses.get(lfile, "  ")
            if code != "  ":
                code = code.replace(" ", "_")

            for stat in "UD?!MACRrd":
                if stat in code:
                    color = glslib.config.mapping[stat]
                    prefix = glslib.config.color[color]
                    break

            else:
                prefix = glslib.config.color["white"]

            if "r" in code or "d" in code:
                postfix = glslib.config.color["grey"] + "<-"
                if os.access(lfile, os.X_OK):
                    next_exec = True

            elif os.access(lfile, os.X_OK) or next_exec:
                postfix = glslib.config.color["green"] + "* "
                next_exec = False

            elif os.path.islink(lfile):
                postfix = glslib.config.color["cyan"] + "^ "

            else:
                postfix = "  "

        out.append(prefix + os.path.basename(lfile) + postfix)
        out_names.append(lfile)

    return out


def format_files_expanded(lfiles, git_status, sys_status):
    
    lengths = max([[len(s) for s in status] for status in sys_status])
    template = "*-%ds *-%ds *-%ds *%ds *-%ds *%ds " % tuple(lengths)
    template = template.replace("*", "%")

    formated_files = format_files(lfiles, git_status)

    outs = []
    for lfile, syss, ffile in zip(lfiles, sys_status, formated_files):
        gits = git_status.get(lfile, "  ")
        gits = gits != "TT" and gits or "  "
        out = template % syss
        out = glslib.config.color["white"] + out
        out = out + ffile
        outs.append(out)

    outs = "\n".join(outs)
    return outs
    


def format_table(files, lengths, disp_width=None):
    """
Format table for output.

Args:
    files (list) : Ready processed file names.
    lengths (list) : length reserved for each file.
    disp_width (int) : Width of the terminal.

Returns:
    (str) : A ready to print output.
    """

    if not disp_width:
        proc = subprocess.Popen('tput cols', shell=1, stdout=-1)
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
    for length, name in zip(lengths, files):

        out += name + " "*(sizes[i]-length)
        i += 1
        if i == n_cols:
            out += "\n"
            i = 0

    if out and out[-1] == "\n":
        out = out[:-1]

    return out


def expand_glob(lpaths, gpaths):
    """
Expand a list of filenames/dirnames/globs.

Args:
    lpaths (list) : Unaltered user input with globs.
    gpaths (list) : List of full paths from git working tree.

Returns:
    (list) : list of expanded paths
    """
    gpaths = sorted(gpaths, key=sorting_key)
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
    add = seen.add
    out = [x for x in out if not (x in seen or add(x))]
    if "" in out:
        out.remove("")

    return out


def get_git_roots(lfiles):
    """
Expand all globs and retrive all unique folders to extract all git root
folders.

Args:
    lfiles (list) : List of unmodified user input.

Returns:
    (dict) : Keys are path names retrieved from globing, and values are the
            assosiated git root folder. The values are empty strings for globs
            outside the repo.
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
    repo_paths = {
        folder : os.path.dirname(
            os.path.abspath(
                git_command(cmd, folder)
            )
        ) + os.sep
        for folder in set(folders)
    }

    return repo_paths


def get_git_status(git_paths):
    """
Get all git files and their status for given set of git repo rot directories.

Args:
    git_paths (list) : List of paths to git repo roots.

Returns:
    (dict) : Keys are full paths, and values are git two-letter status codes.
    """

    if "" in git_paths:
        git_paths.remove("")

    out = {}
    cmd = "git status --ignored --porcelain -u ."
    regex1 = re.compile(r"^(..) ([^ ]*)$", re.M)
    regex2 = re.compile(r"^(..) ([^ ]*) -> (.+)$", re.M)

    for git_path in git_paths:

        statuses = git_command(cmd, git_path)

        out.update({
            git_path + key[1] : key[0]
            for key in re.findall(regex1, statuses)
        })
        out.update({
            git_path + key[1] : key[0] + git_path + key[2]
            for key in re.findall(regex2, statuses)
        })

    return out


def get_sys_status(lfiles, human=False):

    six_months_ago = time.time() - 180*24*60
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
        mode = pre + "".join([m=="1" and M or "-"
                              for m, M in zip(mode, "rwxrwxrwx")])
        stat = os.stat(lfile)
        owner = pwd.getpwuid(stat.st_uid).pw_name
        group = pwd.getpwuid(stat.st_gid).pw_name
        size = stat.st_size
        if human:
            for unit in ['','K','M','G','T','P','E','Z']:
                if size < 1024.0:
                    size = "%3.1f%s" % (size, unit)
                    break
                size /= 1024.0
            else:
                size = "%.1fY" % size
            if not unit:
                size = size[:3]

        else:
            size = str(size)

        mtime = time.gmtime(stat.st_atime)
        if mtime > six_months_ago:
            mtime1, mtime2 = time.strftime("%b;%d %H:%I", mtime).split(";")
        else:
            mtime1, mtime2 = time.strftime("%b;%d  %Y", mtime).split(";")

        out.append((mode, owner, group, size, mtime1, mtime2))

    return out


def add_tracked_unmodified(lfiles, statuses):

    folders = [os.path.dirname(j) + os.sep for j in lfiles]
    cmd = "git ls-tree --name-status HEAD"

    for folder in folders:
        paths = git_command(cmd, folder)
        for line in paths.split("\n"):
            if line and folder+line not in statuses:
                statuses[folder + line] = "TT"



def filter_content(lfiles, statuses,
                   hidden=False, untracked=False, ignored=False):
    """
Remove files from list that are supposed to be hidden. In addition, reformat
files related to renaming.

Args:
    lfiles (list) : A list containing a full paths retrieved after glob.
    statuses (dict) : A dictionary containtin all statuses.
    hidden (bool) : If true, remove hidden files (if untracked or ignored) from
                    list.
    untracked (bool) : If true, remove untracked files from list.
    ignored (bool) : If true, remove ignored files from list.

Returns:
    (list) : List of files, where unwanted files are removed, and renames are
             fixed.

Note:
    Statuses are changed in place for renamed in git work tree.
    """
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

    userinput = args.FILE
    if not userinput:
        userinput = ["."]

    git_roots = get_git_roots(userinput)
    git_statuses = get_git_status(set(git_roots.values()))
    lfiles = expand_glob(userinput, set(git_statuses.keys()))

    add_tracked_unmodified(lfiles, git_statuses)

    ignored = True  - args.all - args.ignored
    hidden = True - args.all
    untracked = args.untracked - args.all

    lfiles = filter_content(lfiles, git_statuses,
                       ignored=ignored, hidden=hidden, untracked=untracked)

    groups = []
    folders = [os.path.dirname(j) + os.sep for j in lfiles]

    curdir = os.path.abspath(".")
    titles = []


    curdir_included = False
    if curdir in folders:
        curdir_included = True

        group = []

        while curdir in folders:
            ind = folders.index(curdir)
            group.append(lfiles[ind])
            del folders[ind]
            del lfiles[ind]

        if args.long:
            sys_statuses = get_sys_status(group, args.human_readable)
            group = format_files_expanded(group, git_statuses, sys_statuses)

        else:
            lengths = [len(os.path.relpath(path)) for path in group]
            group = format_files(group, git_statuses)
            group = format_table(group, lengths)

        groups.append(group)

    while folders:
        group = []
        path = folders[0]

        color = glslib.config.mapping["dir"]
        titles.append(
            glslib.config.color[color] + os.path.relpath(path) + "/:")

        while path in folders:

            ind = folders.index(path)
            group.append(lfiles[ind])
            del folders[ind]
            del lfiles[ind]

        if args.long:
            sys_statuses = get_sys_status(group, args.human_readable)
            group = format_files_expanded(group, git_statuses, sys_statuses)

        else:
            lengths = [len(os.path.relpath(path)) for path in group]
            group = format_files(group, git_statuses)
            group = format_table(group, lengths)
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
