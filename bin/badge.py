#!/usr/bin/env python
'''Create a JSON blob for a badge.'''

import sys
import os
import datetime
import hashlib

#-------------------------------------------------------------------------------

BADGE_DESCRIPTIONS = {
    'core'       : ['Core Skills',
                    'Unix shell, version control, programming, and testing'],
    'instructor' : ['Instructor',
                    'Teaching at workshops or online'],
    'organizer'  : ['Organizer',
                    'Organizing workshops and learning groups'],
    'creator'    : ['Creator',
                    'Creating learning materials and other content']
}

BADGE_KINDS = BADGE_DESCRIPTIONS.keys()

JSON_TEMPLATE = '''{
  "recipient" : "%(email)s",
  "salt": "%(salt)s",
  "issued_on" : "%(when)s",
  "badge" : {
    "version" : "0.5.0",
    "name" : "%(name)s",
    "image" : "/img/badges/%(kind)s.png",
    "description" : "%(description)s",
    "criteria" : "/badges/%(kind)s.html",
    "issuer" : {
      "origin" : "http://software-carpentry.org",
      "name" : "Software Carpentry",
      "contact" : "admin@software-carpentry.org"
    }
  }
}'''

USAGE = '''Usage:
%(name)s username email [%(kinds)s] 
''' % {'name' : sys.argv[0], 'kinds' : '|'.join(BADGE_KINDS)}

SALT = 'software-carpentry'
#-------------------------------------------------------------------------------

def main(args):
    '''Main program driver.'''

    if len(sys.argv) < 4: 
        usage()

    username = sys.argv[1]
    email = sys.argv[2] 
    image_src_dir = 'img/badges'

    for kind in sys.argv[3:]:
        website_dir = '.'
        badge_dir = 'badges/'
        create(image_src_dir, website_dir, badge_dir, kind, username, email)

#-------------------------------------------------------------------------------

def usage():
    print USAGE;
    sys.exit(-1)

#-------------------------------------------------------------------------------
def hashEmailAddress(email, salt):
    return 'sha256$' + hashlib.sha256(email + salt).hexdigest();

#-------------------------------------------------------------------------------

def create(image_src_dir, website_dir, badge_dir, kind, username, email):
    '''Create a new badge.  If 'bake' is True, bake a real badge; if it is False,
    just copy the badge image file (for testing).'''

    # Paths
    image_src_path, json_dst_path = \
        _make_paths(website_dir, badge_dir, kind, username, image_src_dir=image_src_dir)

    # When is the badge being created?
    when = datetime.date.today().isoformat()

    # hide the email address
    hashedemail = hashEmailAddress(email, SALT)

    # Create and save the JSON assertion.
    values = {'username'    : username,
              'email'       : hashedemail,
              'salt'        : SALT,
              'kind'        : kind,
              'when'        : when,
              'name'        : BADGE_DESCRIPTIONS[kind][0],
              'description' : BADGE_DESCRIPTIONS[kind][1]}
    assertion = JSON_TEMPLATE % values
    print 'Badge assertion...'
    print assertion

    # Save assertion.
    writer = open(json_dst_path, 'w')
    writer.write(assertion)
    writer.close()
    print 'JSON badge manifest path:', json_dst_path

def _make_paths(website_dir, badge_dir, kind, username,
                image_src_dir=None, cannot_exist=True):
    '''Create, check, and return the paths used by handlers.'''

    # Badge type is recognized.
    assert kind in BADGE_DESCRIPTIONS, \
           'Unknown kind of badge "%s"' % kind

    # Web site directory.
    assert website_dir is not None, \
           'Web site directory "%s" not provided' % website_dir
    assert os.path.isdir(website_dir), \
           'Web site directory "%s" does not exist' % website_dir

    # Full badge directory.
    assert badge_dir is not None, \
           'Badge sub-directory not provided' % badge_dir
    badge_root_dir = os.path.join(website_dir, badge_dir)
    assert os.path.isdir(badge_root_dir), \
           'Badge root directory "%s" does not exist' % badge_root_dir
    badge_kind_dir = os.path.join(badge_root_dir, kind)
    assert os.path.isdir(badge_kind_dir), \
           'Badge kind directory "%s" does not exist' % badge_kind_dir

    # Badge image source.
    if image_src_dir is None:
        image_src_path = None
    else:
        assert os.path.isdir(image_src_dir), \
               'Image source directory "%s" not found' % image_src_dir
        image_src_path = os.path.join(image_src_dir, '%s.png' % kind)
        assert os.path.isfile(image_src_path), \
               'No such image file "%s"' % image_src_path

    # Name of JSON file.
    json_name = '%s.json' % username

    # JSON file.
    json_dst_path = os.path.join(badge_kind_dir, json_name)
    if cannot_exist:
        assert not os.path.isfile(json_dst_path), \
               'JSON file "%s" already exists' % json_dst_path

    return image_src_path, json_dst_path

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
