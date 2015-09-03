#!/usr/bin/env python3
'''
Utilities for site regeneration.
'''

import os
import re
import urllib.request
import ssl
import yaml
import sys
from PyRSS2Gen import RSS2, RSSItem

# Standard name for metadata files.
CONFIG_YML = '_config.yml'

# Template for metadata (in config directory).
STANDARD_YML = 'standard.yml'

# File with badging information
BADGES_YML = 'badges.yml'

# File with instructor airport locations
AIRPORTS_YML = 'airports.yml'

# File containing all published workshops
WORKSHOPS_YML = 'workshops.yml'

# hardcoded API URLs used for getting new versions of YAMLs of badges, airports
# and workshops
BADGES_URL = 'v1/export/badges.yaml'
AIRPORTS_URL = 'v1/export/instructors.yaml'
WORKSHOPS_URL = 'v1/events/published.yaml'

# File containing names of countries for flags.
FLAGS_YML = 'flags.yml'

# File containing cached information about workshops.
WORKSHOP_CACHE = '_workshop_cache.yml'

# File containing cached information about issues and pull requests.
DASHBOARD_CACHE = '_dashboard_cache.yml'

# Patterns used to extract content and excerpts from compiled blog
# entries.  Using regular expressions is a hack, but is *much* simpler
# than trying to parse and un-parse the not-quite HTML.
P_BLOG_CONTENT = re.compile(r'<!--\s+start\s+content\s+-->\s+(.+)\s+<!--\s+end\s+content\s+-->', re.DOTALL)
P_BLOG_EXCERPT = re.compile(r'<!--\s+start\s+excerpt\s+-->\s+(.+)\s+<!--\s+end\s+excerpt\s+-->', re.DOTALL)

#----------------------------------------

def harvest_metadata(filename):
    '''Harvest metadata from a single file.'''

    try:
        with open(filename, 'r') as reader:
            text = reader.read()
            stuff = text.split('---')[1]
            meta_dict = yaml.load(stuff)
            meta_dict['path'] = filename
            return meta_dict
    except Exception as e:
        print >> sys.stderr, 'Failed to harvest metadata from "{0}": {1}'.format(filename, str(e))
        raise e

#----------------------------------------

def load_info(folder, filename=CONFIG_YML):
    '''Load metadata info file from specified directory and return content.'''
    path = os.path.join(folder, filename)
    assert os.path.isfile(path), \
           'No info file found in folder "{0}"'.format(folder)
    with open(path, 'r') as reader:
        return yaml.load(reader)


def fetch_info(base_url, url):
    """Download a file and save it."""
    address = base_url + url

    # loads operating system's trusted CA certificates
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

    with urllib.request.urlopen(address, context=ssl_context) as f:
        content = f.read()
    return yaml.load(content.decode('utf-8'))


def fetch_workshops_info(base_url, url):
    """Download a file with workshops data and save it.

    Mark workshops 'safe for production' (ie. having specific set of fields
    non-blank)."""
    content = fetch_info(base_url, url)
    for E in content:
        # Some events are considered "published" by AMY even though some of
        # their fields are empty.  This function checks if events are published
        # in the sense that they can be used in this site.
        if (E['start'] and E['end'] and E['slug'] and E['venue']
                and E['address'] and E['country'] and E['latitude']
                and E['longitude'] and E['url'] and E['humandate']):
            E['_published'] = True
        else:
            E['_published'] = False
    return content

#----------------------------------------

class ContentEncodedRSS2(RSS2):
    '''Represent an RSS2 feed with content-encoded items.'''

    def __init__(self, **kwargs):
        RSS2.__init__(self, **kwargs)
        self.rss_attrs['xmlns:content']='http://purl.org/rss/1.0/modules/content/'
        self.rss_attrs['xmlns:dc']='http://purl.org/dc/elements/1.1/'

#----------------------------------------

class ContentEncodedRSSItem(RSSItem):
    '''Represent a single item in an RSS2 feed with content encoding.'''

    def __init__(self, **kwargs):
        self.dc = 'http://purl.org/dc/elements/1.1/'
        self.content = kwargs.get('content', None)
        if 'content' in kwargs:
            del kwargs['content']
        self.creator = kwargs.get('creator', None)
        if 'creator' in kwargs:
            del kwargs['creator']
        RSSItem.__init__(self, **kwargs)

    def publish_extensions(self, handler):
        if self.creator:
          handler.startElement('dc:creator', {})
          handler.characters(self.creator)
          handler.endElement('dc:creator')
        if self.content:
            if hasattr(handler, '_out'):
                writer = handler._out.write
            elif hasattr(handler, '_write'):
                writer = handler._write
            else:
                assert False, \
                       'XML handler does not have _out or _write'
            writer('<%(e)s><![CDATA[%(c)s]]></%(e)s>' %
                   { 'e':'content:encoded', 'c':self.content})
