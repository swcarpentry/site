#!/usr/bin/env python3
'''Get workshop URLs from cached workshop info.'''
import sys
import yaml

def main():
    '''Main driver.'''
    workshops = yaml.load(sys.stdin)
    for w in workshops:
        print(w['slug'], w['url'])

if __name__ == '__main__':
    main()
