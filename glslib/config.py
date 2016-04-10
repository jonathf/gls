

# Color palete
color = {
    "white":    "\033[00m",
    "White":    "\033[1;00m",
    "grey":     "\033[90m",
    "Grey":     "\033[1;90m",
    "red":      "\033[91m",
    "Red":      "\033[1;91m",
    "green":    "\033[92m",
    "Green":    "\033[1;92m",
    "yellow":   "\033[93m",
    "Yellow":   "\033[1;93m",
    "blue":     "\033[94m",
    "Blue":     "\033[1;94m",
    "magenta":  "\033[95m",
    "Magenta":  "\033[1;95m",
    "cyan":     "\033[96m",
    "Cyan":     "\033[1;96m",
}

# Status assignment
mapping = {
    " ":    "white",
    "T":    "white",

    "_":    "grey",
    "?":    "grey",
    "!":    "grey",

    "D":    "red",
    "R":    "red",
    "d":    "red",

    "r":    "magenta",

    "M":    "yellow",

    "A":    "green",

    "dir":  "Blue",

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
