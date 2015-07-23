#!/usr/bin/env python
'''
Create workshop-feed.xml for RSS feed for Software Carpentry 
workshops.
'''

import datetime
import os
import sys
from optparse import OptionParser
from PyRSS2Gen import Category, Guid
from util import ContentEncodedRSS2, ContentEncodedRSSItem
from urllib.parse import urlparse
from util import load_info

#----------------------------------------

def main():
    '''Main driver for workshop feed regeneration.'''

    options, args = parse_args()
    config = load_info(os.curdir)
    config['site'] = options.site

    workshops = get_future_workshops(config['workshops'])
    build_workshop_rss(config,
                       os.path.join(options.output, 'workshop-feed.xml'),
                       workshops)

#----------------------------------------

def parse_args():
    '''Parse command-line arguments.'''

    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output', help='output directory')
    parser.add_option('-s', '--site', dest='site', help='base site URL')
    parser.add_option('-v', '--verbose', dest='verbose', help='enable verbose logging',
                      default=False, action='store_true')
    options, args = parser.parse_args()
    return options, args

#----------------------------------------

def build_workshop_rss(config, filename, workshops):
    '''
    Generate RSS2 file for workshops given the metadata blobs for
    recent workshops.
    '''
    site = config['site']
    publish_time = datetime.datetime.now()
    # Create RSS items.
    try:
        items = [ContentEncodedRSSItem(title=bc['venue'],
                                       creator=bc['contact'],
                                       guid=get_guid(site, bc),
                                       link=bc['url'],
                                       description=get_description(bc),
                                       categories=[get_country(site, bc)],
                                       pubDate=publish_time)
                 for bc in workshops]
    except KeyError as e:
        print('Failed to find key {0} in {1}'.format(str(e), bc), file=sys.stderr)
        sys.exit(1)

    # Create RSS feed.
    rss = ContentEncodedRSS2(title='Software Carpentry workshops',
                             description='Helping researchers do more, in less time, with less pain',
                             lastBuildDate=datetime.datetime.utcnow(),
                             link=site,
                             items=items)

    # Save.
    with open(filename, 'w') as writer:
        rss.write_xml(writer)

def get_future_workshops(workshops):
    '''
    Create a list of workshops that are in the future and return these
    in reverse chronological order.
    '''
    publish_date = datetime.datetime.now().date()
    workshops = [bc for bc in workshops if bc['startdate'] >= publish_date]
    workshops.reverse()
    return workshops

def get_guid(site, workshop):
    '''
    Create non-permalink Guid consisting of Software Carpentry 
    site URL and workshop identifier ('slug').
    '''
    return Guid('{0}/{1}'.format(site, workshop['slug']), 
                isPermaLink=False)

def get_country(site, workshop):
    '''
    Create 'country' category in domain 
    http://software-carpentry.org/locations with workshop's country
    as value.
    '''
    return Category(workshop['country'], 
                    '{0}/{1}'.format(site, 'locations'))

def get_description(workshop):
    '''
    Create description string with workshop date, address (if known)
    and instructors (if known).
    '''
    address = ''
    if workshop.get('address'):
        address = u'at {0}'.format(workshop['address'])
    instructors = ''
    if workshop.get('instructor'):
        instructors = u'led by {0}'.format(u','.join(workshop['instructor']))
    return u'A workshop will be held on {0} {1} {2}'.format(
        workshop['humandate'], address, instructors)

#----------------------------------------

if __name__ == '__main__':
    main()
