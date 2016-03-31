GLS - Git LiSt
===============

`gls` is a `ls`-clone that aims at displaying information about GIT statuses as
part of directory viewing.

Usage
-----
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
------------

Run as root:
```
python setup.py install
```

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

Compatability
-------------

The executable is a python script, so it only works in Linux/Mac.
(However, a one line batch script: `python c:\path\to\gls` should be possible
in Windows.)

Roadmap
-------

* Globbing. Currently it only supports folder targets. But should be doable.
