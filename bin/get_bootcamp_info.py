"""
Download information about bootcamps from GitHub.  The arguments are a
YAML file lising GitHub repository URLs (see config/bootcamp_urls.yml
for an example) and the output file (usually _bootcamp_cache.yml).
"""

import sys
import yaml
import requests

GITHUB_IO_TEMPLATE = 'http://swcarpentry.github.io/{0}/'

REQUIRED_KEYS = set('country humandate startdate url venue'.split())

def main(args):
    '''Main driver.'''

    reader, writer = setup(args)
    all_urls = yaml.load(reader)

    results, all_clean = process(all_urls)
    if not all_clean:
        print >> sys.stderr, 'Not writing result'
        sys.exit(1)

    yaml.dump(results, writer)
    reader.close()
    writer.close()

def setup(args):
    '''Parse command-line arguments and return input and output streams.'''
    reader = sys.stdin
    writer = sys.stdout
    if len(args) > 0:
        reader = open(args[0], 'r')
    if len(args) > 1:
        writer = open(args[1], 'w')
    return reader, writer

def process(all_urls):
    '''
    Process URLs, returning list of info structures and flag
    signalling whether they are all valid.
    '''
    results = []
    all_clean = True
    for url in all_urls:
        info = fetch(url)
        info['slug'] = url.split('/')[-1]
        info['url'] = GITHUB_IO_TEMPLATE.format(info['slug'])
        all_clean =  check_info(url, info) and all_clean
        results.append(info)
    return results, all_clean

def fetch(url):
    '''Fetch information from a single online repository.'''
    url = url.replace('github.com', 'raw.github.com') + '/gh-pages/index.html'
    response = requests.get(url)
    header = response.text.split('---')[1]
    info = yaml.load(header)
    return info

def check_info(url, info):
    '''Check that all required information for bootcamp is present.'''
    missing = REQUIRED_KEYS - set(info.keys())
    if missing:
        missing = sorted(list(missing))
        print >> sys.stderr, 'Info for {0} missing key(s): {1}'.format(url, missing)
        return False
    return True

if __name__ == '__main__':
    main(sys.argv[1:])
