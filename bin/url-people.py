#!/usr/bin/env python3
'''Get instructors and helpers given workshop URL.'''

import sys
from workshops import fetch, check_info, convert_url

for url in sys.argv[1:]:
    url = convert_url(url)
    info = fetch(url)
    print(url)
    for key in ('instructor', 'helper'):
        for item in info[key]:
            print(key, item)
