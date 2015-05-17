#!/usr/bin/env python
'''Get workshop URLs from _config.yml.'''
import sys
import yaml

def main():
    '''Main driver.'''
    workshops = yaml.load(sys.stdin)
    for w in workshops:
        print(w['slug'], w['url'])

if __name__ == '__main__':
    main()
