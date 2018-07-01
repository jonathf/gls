#!/usr/bin/env python
# encoding: utf8
"""
Installer of GLS
"""

import sys
import shutil

from distutils.core import setup

setup(
    name='gls',
    version='0.3.1',
    packages=['glslib'],
    scripts=['gls'],
    url='http://github.com/jonathf/gls',
    author="Jonathan Feinberg",
    author_email="jonathan@xal.no",
)
