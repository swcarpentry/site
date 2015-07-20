#!/usr/bin/env python3
'''Check the index.html data of a workshop given its URL.'''

import sys
from workshops import fetch, check_info, convert_url

assert len(sys.argv) == 2, 'Usage: url-check.py url'
url = convert_url(sys.argv[1])
info = fetch(url)
info['url'] = url
if check_info(url, info):
    print(url)
else:
    print('FAIL:', url)
