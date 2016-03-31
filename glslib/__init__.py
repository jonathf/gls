"""
GLS -- Git list files

A ls-clone that weaves git-status information into output.
"""
import os

import glslib.color
import glslib.git
import glslib.globbing

def main(args):

    # check if in a git repo and default to ls if not
    isgit = os.system(
        "[ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1")
    if isgit != 0:
        sys.exit(os.system("ls --color=auto"))

    if args.recursive:

        for path, dirs, files in os.walk(args.FILE):

            for i in xrange(len(dirs)-1, -1, -1):
                if dirs[i] == ".git":
                    del dirs[i]

            print(glslib.color[mapping["dir"]] + path)
            args.FILE = path
            main(args)
        return

    gpath, lpath, files = glslib.globbing.get_files(args.FILE)

    statuses = glslib.git.get_statuses(gpath, lpath)

    if args.verbose:
        print("paths")
        print(gpath, lpath)
        print("before")
        print(files)
        print(statuses)


    if args.all:
        pass

    elif args.almost_all:
        glslib.git.remove_hidden(files, statuses)

    elif args.untracked:
        glslib.git.remove_hidden(files, statuses)
        glslib.git.remove_ignored(files, statuses)
        glslib.git.remove_untracked(files, statuses)

    else:
        glslib.git.remove_hidden(files, statuses)
        glslib.git.remove_ignored(files, statuses)

    glslib.git.add_renamed(files, statuses)

    lengths = [len(f) for f in files]
    glslib.color.add_color(files, statuses)

    if args.verbose:
        print("after")
        print(files)
        print(statuses)

    print(glslib.color.format_table(files, statuses, lengths, args.width))

