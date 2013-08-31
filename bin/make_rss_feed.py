#!/usr/bin/env python
'''
Create feed.xml for Software Carpentry blog.
'''

import os
import datetime
from PyRSS2Gen import RSS2, RSSItem
from optparse import OptionParser
from util import CONFIG_YML, STANDARD_YML, P_BLOG_CONTENT, P_BLOG_EXCERPT, load_info
#----------------------------------------

def main():
    '''Main driver for feed regeneration.'''

    options, args = parse_args()
    config = load_info(os.curdir)
    config['site'] = options.site
    config['output'] = options.output

    selection = config['blog'][-config['recent_length']:]
    selection.reverse()
    build_blog_rss(config,
                   os.path.join(options.output, 'feed.xml'),
                   selection)
    
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

def build_blog_rss(config, filename, all_posts):
    '''
    Generate RSS2 feed.xml file for blog given the metadata blobs for
    recent posts.
    '''

    # Fill in rendered content and excerpt.
    for p in all_posts:
        p['content'], p['excerpt'] = get_blog_content_excerpt(config, p['path'])

    # Create RSS items.
    site = config['site']
    items = [ContentEncodedRSSItem(title=p['title'],
                                   creator=p['author'],
                                   link=os.path.join(site, p['path']),
                                   description=p['excerpt'],
                                   content=p['content'],
                                   pubDate=datetime.datetime.fromordinal(
                                     p['date'].toordinal()))
             for p in all_posts]

    # Create RSS feed.
    rss = ContentEncodedRSS2(title=config['blog_title'],
                             description=config['blog_subtitle'],
                             lastBuildDate=datetime.datetime.utcnow(),
                             link=site,
                             items=items)

    # Save.
    with open(filename, 'w') as writer:
        rss.write_xml(writer)

#----------------------------------------

def get_blog_content_excerpt(config, filename):
    '''
    Extract page content and excerpt from compiled blog post.  This
    expects the template for blog posts to include comments:
    <!-- start content -->
    <!-- start excerpt -->
    and
    <!-- end excerpt -->
    <!-- end content -->
    The 'content' marker is in the blog post template, so it should
    always be present.  The 'excerpt' markers have only been added
    starting in May 2013; earlier blog posts no longer have excerpts
    included in feed.xml, so this function may return None for them.
    '''
    path = os.path.join(config['output'], filename)
    with open(path, 'r') as reader:
        temp = reader.read()
        temp = P_BLOG_CONTENT.search(temp)
        assert temp, \
               'Blog entry "{0}" lacks content markers'.format(path)
        content = temp.group(1)

        temp = P_BLOG_EXCERPT.search(content)
        excerpt = None
        if temp:
            excerpt = temp.group(1)

        return content, excerpt

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
                   { 'e':'content:encoded', 'c':unicode(self.content)})

#----------------------------------------

if __name__ == '__main__':
    main()
