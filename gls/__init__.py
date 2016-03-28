import sys
from subprocess import Popen
import glob
import os
import sys
import functools

from gls.configure import color, white, mapping


def get_git_status(gitpath, path):

    os.chdir(gitpath+path)
    if sys.version_info.major == 2:
        proc = Popen("git status --ignored --porcelain -u .", shell=True, stdout=-1)
        status = proc.communicate()[0].split("\n")[:-1]
        status = {d[4+len(path):]: d[:2] for d in status
                if d[-1] != "/"}
    else:
        with Popen("git status --ignored --porcelain -u .",
                   shell=True, stdout=-1) as proc:
            status = proc.stdout.read().decode("utf-8")
            status = status.split("\n")[:-1]
            status = {d[4+len(path):]: d[:2] for d in status
                    if d[-1] != "/"}

    if "" in status:
        del status[""]

    for key in list(status.keys()):
        if "/" in key:
            del status[key]
    return status


def format_status(status):
    X, Y = status
    if X == " ":
        X = "_"
    if Y == " ":
        Y = "_"
    if X == Y == "_":
        X = Y = " "
    return X, Y

def word_color(X, Y):

    Z = X+Y
    for code in "UD?!MACR":
        if code in Z:
            return color[mapping[code]]

    return white


def main(args):

    path = os.path.abspath(args.DIR)
    os.chdir(path)
    gitpath = Popen("git rev-parse --git-dir .",
                    shell=1, stdout=-1).communicate()[0][:-7]
    if sys.version_info.major == 3:
        gitpath = gitpath.decode("utf-8")
    path = path[len(gitpath):]

    files = glob.glob(gitpath+path+"/*")
    files += glob.glob(gitpath+path+"/.*")
    files = [f[len(gitpath+path)+1:] for f in files]

    if ".git" in files:
        del files[files.index(".git")]

    def _cmp(lhs, rhs):
        while lhs and lhs[0] == ".":
            lhs = lhs[1:]
        while rhs and rhs[0] == ".":
            rhs = rhs[1:]

        return 1*(lhs == rhs) + 1*(lhs < rhs) - 1

    if sys.version_info.major == 2:
        files.sort(cmp=_cmp)
    else:
        files = sorted(files, key=functools.cmp_to_key(_cmp))

    lengths = [len(f) for f in files]
    prefix = [white + "  "]*len(files)

    if args.verbose:
        print("before")
        print(files)

    # retrieve all files in repo with status
    git_status = get_git_status(gitpath, path)
    if args.verbose:
        print("status")
        print(git_status)

    for i in range(len(files)-1, -1, -1):

        file = files[i]
        if os.path.isdir(file):
            prefix[i] = color[mapping["dir"]] + "  "
            continue

        if file in git_status:
            X, Y = format_status(git_status.pop(file))
        else:
            X, Y = format_status("  ")

        if args.all:
            pass

        elif os.path.split(file)[-1][0] == "." and X in "!?"\
                and not args.all:
            del files[i]
            del prefix[i]
            del lengths[i]
            continue

        elif args.almost_all:
            pass

        elif not args.ignored and X == "!":
            del files[i]
            del prefix[i]
            del lengths[i]
            continue

        elif not args.untracked and X == "?":
            del files[i]
            del prefix[i]
            del lengths[i]
            continue

        cX = color[mapping[X]]
        cY = color[mapping[Y]]
        cZ = word_color(X, Y)
        prefix[i] = cX + X + cY + Y + cZ

    if args.verbose:
        print("between")
        print(files)

    for file, status in git_status.items():

        X, Y = format_status(status)

        if file[0] == "." and X in "!?"\
                and not args.all:
            if file in files:
                index = files.index(file)
                del files[index]
                del prefix[index]
                del lengths[index]
            continue
        elif args.almost_all:
            pass
        elif not args.ignored and X == "!":
            if file in files:
                index = files.index(file)
                del files[index]
                del prefix[index]
                del lengths[index]
            continue
        elif not args.untracked and X == "?":
            if file in files:
                index = files.index(file)
                del files[index]
                del prefix[index]
                del lengths[index]
            continue

        cX = color[mapping[X]]
        cY = color[mapping[Y]]
        cZ = word_color(X, Y)
        prefix.append(cX + X + cY + Y + cZ)
        lengths.append(len(file))
        files.append(file)

    if args.verbose:
        print("after")
        print(files)

    for i in range(len(files)-1, -1, -1):
        if " -> " in files[i]:
            f1, f2 = files[i].split(" -> ")
            index = files.index(f2)
            files[index] = files[index] + color["grey"] + "<-" + f1
            lengths[index] += lengths[i] + 2

            del files[i]
            del prefix[i]
            del lengths[i]

    if args.width:
        width = args.width
    else:
        proc = Popen('tput cols', shell=1, stdout=-1)
        width = int(proc.communicate()[0])

    if args.verbose:
        print("width", width)

    print(format_table(files, prefix, lengths, width))


def format_table(files, prefix, lengths, disp_width):
    "format table for output"

    max_name_width = max(lengths)
    n_cols = int(disp_width / (max_name_width+2))

    sizes = [2]*n_cols
    i = 0
    while lengths:
        length = lengths.pop(0)
        sizes[i] = sizes[i] < length and length or sizes[i]
        i += 1
        if i == n_cols:
            i = 0

    out = ""
    i = 0
    while files:
        name = files.pop(0)
        pre = prefix.pop(0)
        out += pre + name.ljust(sizes[i])+" "
        i += 1
        if i == n_cols:
            out += "\n"
            i = 0

    return out + color["white"]

