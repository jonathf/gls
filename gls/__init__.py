"""
GLS -- Git list files

A ls-clone that weaves git-status information into output.
"""
import gls.color
import gls.git
import gls.globbing

def main(args):

    gpath, lpath, files = gls.globbing.get_files(args.FILE)

    statuses = gls.git.get_statuses(gpath, lpath)

    if args.verbose:
        print("paths")
        print(gpath, lpath)
        print("before")
        print(files)
        print(statuses)


    if args.all:
        pass

    elif args.almost_all:
        gls.git.remove_hidden(files, statuses)

    elif args.untracked:
        gls.git.remove_hidden(files, statuses)
        gls.git.remove_ignored(files, statuses)
        gls.git.remove_untracked(files, statuses)

    else:
        gls.git.remove_hidden(files, statuses)
        gls.git.remove_ignored(files, statuses)

    gls.git.add_renamed(files, statuses)

    lengths = [len(f) for f in files]
    gls.color.add_color(files, statuses)

    if args.verbose:
        print("after")
        print(files)
        print(statuses)

    print(gls.color.format_table(files, statuses, lengths, args.width))

