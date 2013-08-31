#!/usr/bin/env python

"""
Display all the author names used in blog posts.
Usage: authors.py $(ls blog/????/??/*.html)
"""

import sys
from util import harvest_metadata

names = set()
for filename in sys.argv[1:]:
    names.add(harvest_metadata(filename)['author'])
for n in sorted(names):
    print n
