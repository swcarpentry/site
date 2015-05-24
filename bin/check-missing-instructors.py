#!/usr/bin/env python

'''Which badged instructors do *not* have a biography posted?'''

import sys
import yaml
import os

assert len(sys.argv) >= 3, 'Usage: {0} yaml_file biography [biography...]'.format(sys.argv[0])
config, filenames = sys.argv[1], sys.argv[2:]

expected = [entry['user'] for entry in yaml.load(open(config, 'r'))['instructor']]

filenames = [os.path.splitext(os.path.split(f)[1])[0] for f in filenames]

for m in sorted(set(expected) - set(filenames)):
    print(m)
