#!/usr/bin/env python

"""
Display all the categories used in blog posts.
Usage: categories.py $(ls blog/????/??/*.html)
"""

import sys
from collections import defaultdict
from util import harvest_metadata

categories = defaultdict(set)
for filename in sys.argv[1:]:
    these = harvest_metadata(filename)['category']
    for t in these:
        categories[t].add(filename)
for k in sorted(categories.keys()):
    print '{0}: {1}'.format(k, ', '.join(categories[k]))
