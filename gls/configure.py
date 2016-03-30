
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
