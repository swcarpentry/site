#!/usr/bin/env python3
'''List Eventbrite keys for workshops.'''
import sys
import yaml

def main():
    '''Main driver.'''
    everything = yaml.load(sys.stdin)
    workshops = everything['workshops']
    for w in workshops:
        e = w.get('eventbrite', None)
        if e:
            print w['slug'], e

if __name__ == '__main__':
    main()
