#!/usr/bin/env python
""" gls: git-listings

A ls-clone that lists a content of a folder using the logic of ls,
but displayes the git-status through the colors."""

import argparse
import os
import sys
import gls

def argument_parser():

    descriptions = []
    for description in sorted(gls.configure.description.keys()):

        code = gls.configure.description[description]
        mapping = gls.configure.mapping[code]
        color = gls.configure.color[mapping]
        description = "     * " + color + description
        description = description + gls.configure.color["white"]
        descriptions.append(description)

    descriptions = "\n".join(descriptions)


    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="""\
    List information in DIR and color them by git local status""",
        epilog="""The default setting is to hide files that are
    ignored and untracked.
    Tracked hidden files are always visible.

    The colors have the following meaning:
"""+descriptions+"""
    Tracked files without change are white.""",
        usage="%(prog)s [-aAihlruvV] DIR"
        )

    parser.add_argument("FILE", nargs="?",
                        help="files to list")
    parser.add_argument("-A", "--all", action="store_true",
                        help="show untracked, ignored and hidden")
    parser.add_argument("-a", "--almost-all", action="store_true",
                        help="show untracted and ignored")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="list subdirectories recursively")
    parser.add_argument("-u", "--untracked", action="store_true",
                        help="show untracked files")
    parser.add_argument("-i", "--ignored", action="store_true",
                        help="show ignored files")
    parser.add_argument("-s", "--server", action="store_true",
                        help="check status on server instead of local")
    parser.add_argument("-d", "--directory", action="store_true",
                        help="do not include directories")
    parser.add_argument("-w", "--width", type=int,
                        help="assume screen width instead of current value")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="be loud")

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = argument_parser()

    # check if in a git repo and default to ls if not
    isgit = os.system(
        "[ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1")
    if isgit != 0:
        sys.exit(os.system("ls --color=auto"))

    if args.recursive:

        for path, dirs, files in os.walk(args.DIR):

            for i in xrange(len(dirs)-1, -1, -1):
                if dirs[i] == ".git":
                    del dirs[i]

            print(gls.color[mapping["dir"]] + path)
            args.DIR = path
            gls.main(args)

    else:
        gls.main(args)
