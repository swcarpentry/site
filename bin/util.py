#!/usr/bin/env python
'''
Utilities for site regeneration.
'''

import os
import re
import yaml

# Standard name for metadata files.
CONFIG_YML = '_config.yml'

# Template for metadata (in config directory).
STANDARD_YML = 'standard_config.yml'

# Configuration file generated from admin database with badging information (in config directory).
BADGES_YML = 'badges_config.yml'

# File generated from admin database with instructor airport locations (in config directory).
AIRPORTS_YML = 'airports_config.yml'

# File containing URLs for bootcamp repositories (in config directory).
BOOTCAMP_URLS_YML = 'bootcamp_urls.yml'

# File containing cached information about bootcamps.
BOOTCAMP_CACHE = '_bootcamp_cache.yml'

# Patterns used to extract content and excerpts from compiled blog
# entries.  Using regular expressions is a hack, but is *much* simpler
# than trying to parse and un-parse the not-quite HTML.
P_BLOG_CONTENT = re.compile(r'<!--\s+start\s+content\s+-->\s+(.+)\s+<!--\s+end\s+content\s+-->', re.DOTALL)
P_BLOG_EXCERPT = re.compile(r'<!--\s+start\s+excerpt\s+-->\s+(.+)\s+<!--\s+end\s+excerpt\s+-->', re.DOTALL)

#----------------------------------------

def harvest_metadata(filename):
    '''Harvest metadata from a single file.'''

    with open(filename, 'r') as reader:
        text = reader.read()
        stuff = text.split('---')[1]
        meta_dict = yaml.load(stuff)
        meta_dict['path'] = filename
        return meta_dict

#----------------------------------------

def load_info(folder, filename=CONFIG_YML):
    '''Load metadata info file from specified directory and return content.'''
    path = os.path.join(folder, filename)
    assert os.path.isfile(path), \
           'No info file found in folder "{0}"'.format(folder)
    with open(path, 'r') as reader:
        return yaml.load(reader)
