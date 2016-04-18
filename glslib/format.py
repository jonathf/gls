"""
Module for formating files and statuses into printable enteties.
"""
import os
import subprocess

import glslib.config


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
        code = statuses.get(lfile, "  ")

        if os.path.isdir(lfile):
            color = glslib.config.mapping["dir"]
            prefix = glslib.config.color[color]

        else:
            if code != "  ":
                code = code.replace(" ", "_")

            for stat in "UD?!MACRrd":
                if stat in code:
                    color = glslib.config.mapping[stat]
                    prefix = glslib.config.color[color]
                    break

            else:
                prefix = glslib.config.color["white"]

        if os.path.islink(lfile):
            postfix = glslib.config.color["cyan"] + "^ "

        elif os.path.isdir(lfile):
            postfix = "  "

        elif "r" in code or "d" in code:
            postfix = glslib.config.color["grey"] + "<-"
            if os.access(lfile, os.X_OK):
                next_exec = True

        elif os.access(lfile, os.X_OK) or next_exec:
            postfix = glslib.config.color["green"] + "* "
            next_exec = False

        else:
            postfix = "  "



        out.append(prefix + os.path.basename(lfile) + postfix)
        out_names.append(lfile)

    return out


def format_files_expanded(lfiles, git_status, sys_status):
    """
    Format files for output in --long mode.

    Args:
        lfiles (list) : positional list of filenames.
        git_status (dict) : collection of git-statuses.
        sys_status (list) : positional list of tuple statuses.
    """

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

    return "\n".join(outs)


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
    disp_width = max(max(lengths)+2, disp_width)

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


def format_group(path, folders, lfiles, git_statuses,
                   human=False, long=False, width=None):
    """
Format a list of files/folders for printing.
    """

    group = []

    while path in folders:
        ind = folders.index(path)
        group.append(lfiles[ind])
        del folders[ind]
        del lfiles[ind]

    if long:
        sys_statuses = glslib.globbing.get_sys_status(group, human)
        return format_files_expanded(group, git_statuses, sys_statuses)

    lengths = [len(os.path.relpath(path)) for path in group]
    group = format_files(group, git_statuses)
    return format_table(group, lengths, width)
