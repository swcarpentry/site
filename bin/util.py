#!/usr/bin/env python3
'''
Utilities for site regeneration.
'''

import os
import re
import yaml
from PyRSS2Gen import RSS2, RSSItem

# Standard name for metadata files.
CONFIG_YML = '_config.yml'

# Template for metadata (in config directory).
STANDARD_YML = 'standard.yml'

# Configuration file generated from admin database with badging information (in config directory).
BADGES_YML = 'badges.yml'

# File generated from admin database with instructor airport locations (in config directory).
AIRPORTS_YML = 'airports.yml'

# File containing URLs for workshop repositories (in config directory).
WORKSHOPS_YML = 'workshops.yml'

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

