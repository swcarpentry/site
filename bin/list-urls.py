#!/usr/bin/env python3

'''Get workshop URLs from _config.yml.'''

import sys
import yaml

def main():
    '''Main driver.'''
    config = yaml.load(sys.stdin)
    for w in config['workshops']:
        print(w['slug'], w['url'])

if __name__ == '__main__':
    main()
