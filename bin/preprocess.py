#!/usr/bin/env python
'''
Create _config.yml used to compile Software Carpentry web site.
'''

import sys
import os
import glob
import datetime
import time
import yaml
from optparse import OptionParser
from util import CONFIG_YML, \
                 STANDARD_YML, \
                 AIRPORTS_YML, \
                 BADGES_YML, \
                 BOOTCAMP_URLS_YML, \
                 BOOTCAMP_CACHE, \
                 P_BLOG_EXCERPT, \
                 harvest_metadata, \
                 load_info

# Translate two-digit month identifiers into short names.
MONTHS = {
    '01' : 'Jan', '02' : 'Feb', '03' : 'Mar', '04' : 'Apr',
    '05' : 'May', '06' : 'Jun', '07' : 'Jul', '08' : 'Aug',
    '09' : 'Sep', '10' : 'Oct', '11' : 'Nov', '12' : 'Dec'
}

# Template for recent blog posts.
RECENT_POST = '''\
<h3><a href="{{page.root}}/%(path)s">%(title)s</a></h3>
<div class="row-fluid">
  <span class="span11">
    %(excerpt)s
  </span>
  <span class="span1"></span>
</div>
<div class="row-fluid">
  <span class="span11">Posted %(date)s by %(author)s</span>
  <span class="span1">
    <a href="{{page.root}}/%(path)s">...more</a>
  </span>
</div>
'''

#----------------------------------------

def main():
    '''
    Main driver for regenerating _config.yml for web site.
    This program also creates _includes/recent_blog_posts.html.
    '''

    # Get the standard stuff.
    options, args = parse_args()

    # Check that a cached bootcamp information file is available, and
    # report an error if it's not.  Do this early to avoid wasting
    # time; store in local variable until other bootcamp info is
    # loaded and available for merging.
    cached_bootcamp_info = load_cached_bootcamp_info(os.curdir, BOOTCAMP_CACHE)

    # Load other information.
    config = load_info(options.config_dir, STANDARD_YML)
    config['badges'] = load_info(options.config_dir, BADGES_YML)
    config['airports'] = load_info(options.config_dir, AIRPORTS_YML)
    config.update({
        'month_names'     : MONTHS,
        'months'          : sorted(MONTHS.keys()),
        'site'            : options.site,
        'timestamp'       : time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'today'           : options.today
    })

    # Cache the window size.
    recent_length = config['recent_length']

    # Get information from blog entries.
    config['blog'] = harvest_blog(config)

    # Sanity checks on blog posts.
    check_blog_sanity(config['blog'])

    # Select those that'll be displayed on the home page, the index page, etc.
    config['blog_recent'] = config['blog'][-recent_length:]
    config['blog_recent'].reverse()

    # Create _includes/recent_blog_posts.html for inclusion in blog index page.
    # This is done programmatically because we want snippets to be rendered properly.
    for post in config['blog_recent']:
        post['excerpt'] = get_blog_excerpt(post['path'])
    write_recent_blog_posts(config['blog_recent'])

    # Organize all posts by year and month.
    blog_lookup, blog_count = organize_blog_entries(config['blog'])
    config['blog_lookup'] = blog_lookup
    config['blog_count'] = blog_count
    config['blog_years'] = sorted(blog_lookup.keys())
    config['blog_years'].reverse()

    # Construct list of favorite blog posts.
    config['blog_favorites'] = [p for p in config['blog'] if p['favorite']]
    config['blog_favorites'].reverse()

    # Get information from legacy boot camp pages and merge with cached info.
    config['bootcamps'] = harvest_bootcamps(cached_bootcamp_info)

    # Select those that'll be displayed on the home page.
    upcoming = [bc for bc in config['bootcamps'] if bc['startdate'] >= config['today']]
    config['bootcamps_upcoming'] = upcoming[:recent_length]

    # Save.
    with open(CONFIG_YML, 'w') as writer:
        yaml.dump(config, writer)

#----------------------------------------

def parse_args():
    '''Parse command-line arguments.'''

    parser = OptionParser()
    parser.add_option('-c', '--config', dest='config_dir', help='configuration directory')
    parser.add_option('-o', '--output', dest='output', help='output directory')
    parser.add_option('-s', '--site', dest='site', help='site')
    parser.add_option('-t', '--today', dest='today', help='build date',
                      default=datetime.date.today())
    parser.add_option('-v', '--verbose', dest='verbose', help='enable verbose logging',
                      default=False, action='store_true')
    options, args = parser.parse_args()
    return options, args

#----------------------------------------

def load_cached_bootcamp_info(folder, filename):
    '''Load cached bootcamp info if available, fail if not.'''
    path = os.path.join(folder, filename)
    if not os.path.isfile(path):
        print >> sys.stderr, 'Bootcamp information cache "{0}" does not exist.'.format(path)
        print >> sys.stderr, 'Please use "make cache" before building site,'
        print >> sys.stderr, 'Or run "bin/get_bootcamp_info" to regenerate it.'
        sys.exit(1)
    return load_info(folder, filename)

#----------------------------------------

def harvest_blog(config):
    '''Harvest metadata for all blog entries.'''

    all_meta = []
    for folder in glob.glob('blog/????/??'):
        for post in glob.glob('{0}/*.html'.format(folder)):
            m = harvest_metadata(post)
            m['folder'] = folder
            fill_optional_metadata(m, 'favorite')
            all_meta.append(m)

    all_meta.sort(lambda x, y: cmp(x['date'], y['date']) or cmp(x['time'], y['time']))
    return all_meta

#----------------------------------------

def harvest_bootcamps(bootcamps):
    '''Harvest metadata from all boot camp index.html pages and merge with cached info.'''
    pages = glob.glob('bootcamps/*/index.html')
    metadata = harvest(pages)
    for f in metadata:
        bootcamps.append(metadata[f])
        bootcamps[-1]['slug'] = f.split('/')[1]
        fill_optional_metadata(bootcamps[-1], 'contact')
    bootcamps.sort(lambda x, y: cmp(x['slug'], y['slug']))
    return bootcamps

#----------------------------------------

def harvest(filespec):
    '''
    Get content and metadata from HTML files. Return a single metadata
    dictionary if a single path is given as input, or a dictionary
    mapping filenames to metadata dictionaries if multiple paths are
    given.
    '''

    if isinstance(filespec, basestring):
        return harvest_metadata(filespec)

    elif isinstance(filespec, list):
        return dict([(f, harvest_metadata(f)) for f in filespec])

    else:
        assert False, 'Unknown filespec "{0}"'.format(filespec)

#----------------------------------------

def fill_optional_metadata(post, *fields):
    '''
    Fill in metadata fields that are only provided for some posts.
    '''
    for f in fields:
        if f not in post:
            post[f] = None

#----------------------------------------

def check_blog_sanity(posts):
    '''Make sure all blog posts have sensible metadata.'''
    seen = {}
    errors = False
    for p in posts:
        timestamp = (p['date'], p['time'])
        if timestamp in seen:
            print >> sys.stderr, 'Timestamp {0} in {1} duplicated in {2}'.format(timestamp, seen[timestamp], p['path'])
            errors = True
        else:
            seen[timestamp] = p['path']
    if errors:
        sys.exit(1)

#----------------------------------------

def organize_blog_entries(posts):
    '''Organize blog entries by year and month.'''

    blog_lookup = {}
    blog_count = {}
    for p in posts:
        year = '%4d' % p['date'].year
        month = '%02d' % p['date'].month
        if year not in blog_lookup:
            blog_lookup[year] = dict([(m,list()) for m in MONTHS.keys()])
            blog_count[year] = dict([(m,0) for m in MONTHS.keys()])
        blog_lookup[year][month].append(p)
        blog_count[year][month] += 1
    return blog_lookup, blog_count

#----------------------------------------

def get_blog_excerpt(path):
    '''Get excerpt from blog post for inclusion in blog index page.'''
    with open(path, 'r') as reader:
        temp = reader.read()
        temp = P_BLOG_EXCERPT.search(temp)
        assert temp, 'Blog post {0} lacks excerpt'.format(path)
        return temp.group(1)

#----------------------------------------

def write_recent_blog_posts(posts):
    '''Write out recent blog posts for inclusion in blog index page.'''
    with open('_includes/recent_blog_posts.html', 'w') as writer:
        for p in posts:
            print >> writer, RECENT_POST % p

#----------------------------------------

if __name__ == '__main__':
    main()
