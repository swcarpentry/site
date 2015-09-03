#!/usr/bin/env python3
'''Get instructors per workshop from cached workshop info.'''
import sys
import yaml

def main():
    '''Main driver.'''
    workshops = yaml.load(sys.stdin)
    for b in workshops:
        for i in b['instructor']:
            print(b['slug'], i)

if __name__ == '__main__':
    main()
