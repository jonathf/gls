GLS - Git LiSt
==============

`gls` is a `ls`-clone that aims at displaying information about GIT statuses as
part of directory viewing.

Usage
=====
It works about the same as `ls`. In fact, if not in a `git` repository, it
defaults to using builtin `ls`. However there are some differences.
If a file is hidden (starting with a `.`), but tracked, it is by default shown
by `gls`. Reversely, if a file is ignored (irrespectively if it is starts with
`.` or not), it is hidden from default view.

The colors in the output has the following interpretations:

* red - deleted
* blue - directory
* yellow - modified
* green - new
* magenda - renamed
* cyan - unmerged or missmatch in worktree
* white - unmodified
* gray - untracked or ignored

Obviously, this does not give detailed information about what is going on. For
that we have `git status`. But for the day to day activity, it gives quick
and relevant information about the files being edited.

Installation
============

Run as root:
```
python setup.py install
```

Argument completion
-------------------

To enable tabcompletion, installation of `argcomplete` is required.
```
sudo apt-get install python-argcomplete
sudo activate-global-python-argcomplete
```

If installed in Python3:
```
sudo apt-get install python3-argcomplete
sudo activate-global-python-argcomplete3
```

It is possible to install argcomplete using `pip`, but the activation script is
not. It should either be done from package manager or from source:
https://github.com/kislyuk/argcomplete

Globbing
--------
Default behavior when including wildcards `*` as an argument is for the fell to
expand it to a list of all files matching the wildcard expression. This is fine
for `ls`, but if you want to include information about deleted files that
exists in the git tree, then globing should be handled by `gls`.

Intercepting globbing can not be done through the installation process. Instead
one must add a line to the shell configuration file.

In Bash, Sh or Ksh, add the following line to `.bashrc`:
```
alias gls='set -f;gls';gls(){ command gls "$@"; set +f;}
```
In Csh and Tsch:
```
alias gls 'set noglob;`which gls` \!*;unset noglob'
```
And in Zsh:
```
alias gls='noglob `which gls`'
```

Compatability
=============

The executable is a python script, so it only works in Linux/Mac.
(However, a one line batch script: `python c:\path\to\gls` should be possible
in Windows.)
