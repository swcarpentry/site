#!/usr/bin/env python

'''Check consistency of workshop info.'''

import sys
import yaml
from collections import Counter

def main():
    '''Main driver.'''
    assert len(sys.argv) == 3, \
           'Usage: {0} urls_only cached_info'.format(sys.argv[0])

    with open(sys.argv[1]) as reader:
        urls_only = yaml.load(reader)

    with open(sys.argv[2]) as reader:
        cached_info = [x['url'] for x in yaml.load(reader)]

    duplicates = set(urls_only) & set(cached_info)
    if duplicates:
        print('in both upcoming and cached:')
        print('\n'.join(sorted(duplicates)))

    for (source, title) in ((urls_only, 'URLS only'), (cached_info, 'cached info')):
        frequency = Counter(source)
        for key in frequency:
            if frequency[key] > 1:
                print('{0} occurs multiple times in {1}'.format(key, title))

if __name__ == '__main__':
    main()
