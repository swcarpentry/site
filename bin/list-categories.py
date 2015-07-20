#!/usr/bin/env python3

"""
Display all the categories used in blog posts.
Usage: categories.py $(ls blog/????/??/*.html)
"""

import sys
import traceback
from collections import defaultdict
from util import harvest_metadata

show_count, filenames = False, sys.argv[1:]
if filenames[0] == '-n':
    show_count, filenames = True, filenames[1:]

categories = defaultdict(set)
for f in filenames:
    try:
        these = harvest_metadata(f)['category']
        for t in these:
            categories[t].add(f)
    except Exception as e:
        print('Failed in {0}'.format(f), file=sys.stderr)
        traceback.print_exc(None, sys.stderr)
        sys.exit(1)

for k in sorted(categories.keys()):
    if show_count:
        print('{0}: {1}'.format(len(categories[k]), k))
    else:
        print('{0}: {1}'.format(k, len(categories[k])))
