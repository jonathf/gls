import os
import subprocess

# Color palete
color = {
    "white":    "\033[00m",
    "grey":     "\033[90m",
    "red":      "\033[91m",
    "green":    "\033[92m",
    "yellow":   "\033[93m",
    "blue":     "\033[94m",
    "magenta":  "\033[95m",
    "cyan":     "\033[96m",
}

# Status assignment
mapping = {
    " ":    "white",

    "_":    "grey",
    "?":    "grey",
    "!":    "grey",

    "D":    "red",
    "R":    "red",
    "d":    "red",

    "r":    "magenta",

    "M":    "yellow",

    "A":    "green",

    "dir":  "blue",

    "C":    "cyan",
    "U":    "cyan",
}

# Status description
description = {
              "unmodified" : " ",
    "untracked or ignored" : "?",
                 "deleted" : "D",
                "modified" : "M",
                 "renamed" : "r",
                     "new" : "A",
                "directory": "dir",
    "unmerged or missmatch in worktree" : "U",
}

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
            if "r" in (X, Y) or "d" in (X, Y):
                postfix = color["grey"] + "<-"
            else:
                postfix = "  "

        lfiles[i] = prefix + lfiles[i] + postfix + color["white"]


def word_color(status_local, status_server):
    """
    Select color for the status.

Args:
    status_local (str) : Single letter git status code.
    status_server (str) : Single letter git status code.

Returns:
    (str) : Bash color code respective to the color mapping rule.
    """

    for code in "UD?!MACRrd":
        if code in status_local+status_server:
            return color[mapping[code]]

    return color["white"]


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


def format_table(files, statuses, lengths, disp_width=None):
    "format table for output"

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
    for length,name in zip(lengths, files):

        out += name + " "*(sizes[i]-length)
        i += 1
        if i == n_cols:
            out += "\n"
            i = 0

    if out and out[-1] == "\n":
        out = out[:-1]

    return out

