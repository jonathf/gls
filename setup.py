#!/usr/bin/env python
# encoding: utf8

import sys
import shutil

from distutils.core import setup

setup(
    name='gls',
    version='0.1',
    packages=['gls'],
    url='http://github.com/jonathf/gls',
    author="Jonathan Feinberg",
    author_email="jonathan@xal.no",
)

if sys.version_info.major == 2:
    input = raw_input
    src = "gls2.py"
else:
    src = "gls3.py"


def copy_script():

    query = input("[y]es/[n]o/[c]ustom location:")
    query = query[:1].lower()

    if query == "y":
        target = "/usr/local/bin/gls"
        shutil.copy(src, target)

    elif query == "n":
        sys.exit(0)

    elif query == "c":
        target = input("Input path:")
        shutil.copy(src, target)

    else:
        print("please select valid option")
        copy_script()


print("Copy gls script to /usr/local/bin?")
copy_script()
