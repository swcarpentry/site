#!/usr/bin/env python3
"""Create a JSON blob for a badge."""

import sys
import os
import datetime
import hashlib
import json
import badge
import badgebakery

def main(username, email, kind, website_dir):
    """Main program driver."""

    image_src_dir = os.path.join(website_dir, "img", "badges")
    badge_dst_dir = os.path.join(website_dir, "badges")

    create(image_src_dir, badge_dst_dir, kind, username, email)

def create(image_src_dir, badge_dst_dir, kind, username, email):
    """Create JSON and PNG for a new badge."""

    # Paths
    image_src_path, image_dst_path, json_dst_path = \
        make_paths(image_src_dir, badge_dst_dir, kind, username)

    # When is the badge being created?
    when = datetime.date.today().isoformat()

    # Hide the email address
    hashedemail = hash_email_address(email, badge.SALT)

    # Consistent slug combining kind and username.
    slug = "{0}/{1}".format(kind, username)

    # Cache a few values.
    name = kind
    description = badge.BADGE_DESCRIPTIONS[kind][1]
    criteria = "/badges/index.html#{0}.html".format(kind)
    assertion_url = "/badges/{0}.json".format(slug)
    image_url = "/badges/{0}.png".format(slug)

    new_badge = {
        "uid":hashedemail,
        "issuedOn":when,
        "image":badge.set_image_url(name),
        "recipient":{
            "identity":hashedemail,
            "type":"email",
            "hashed":True,
            "salt":badge.SALT},
        "badge":badge.set_badge_url(name),
        "verify":{
            "type":"hosted",
            "url":badge.set_verify_url(name, username)}}

    # Create and save the JSON assertion.
    with open(json_dst_path, "w") as writer:
        json.dump(new_badge, writer, indent=True, sort_keys=True)

    badgebakery.bake_badge("img/badges/{0}.png".format(kind),
            "{0}.png".format(username),
            slug)

def make_paths(image_src_dir, badge_dst_dir, kind, username):
    """Create, check, and return the paths used by handlers."""

    # Badge type is recognized.
    assert kind in badge.BADGE_KINDS, \
           "Unknown kind of badge {0}".format(kind)

    # Output directory.
    assert badge_dst_dir, \
           "Badge sub-directory not provided"
    assert os.path.isdir(badge_dst_dir), \
           "Badge destination directory {0} does not exist".format(badge_dst_dir)

    # Badge image source.
    assert os.path.isdir(image_src_dir), \
           "Image source directory {0} not found".format(image_src_dir)
    image_src_path = os.path.join(image_src_dir, "{0}.png".format(kind))
    assert os.path.isfile(image_src_path), \
           "No such image file {0}".format(image_src_path)

    # Badge image destination.
    image_dst_path = os.path.join(badge_dst_dir, "{0}{1}.png".format(kind, username))
    assert not os.path.isfile(image_dst_path), \
           "Output image {0} already exists".format(image_dst_path)

    # JSON file.
    json_dst_path = os.path.join(badge_dst_dir, "{0}/{1}.json".format(kind, username))
    assert not os.path.isfile(json_dst_path), \
           "JSON file {0} already exists".format(json_dst_path)

    # Report.
    return image_src_path, image_dst_path, json_dst_path

def hash_email_address(email, salt):
    return "sha256$" + hashlib.sha256(email + salt).hexdigest();

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create JSON blob and baked PNG for a badge")
    parser.add_argument("username")
    parser.add_argument("email")
    parser.add_argument("kind",
            choices=["core", "creator", "helper", "instructor", "organizer"])
    parser.add_argument("site_dir", default="", nargs="?")

    args = parser.parse_args()

    main(args.username, args.email, args.kind, args.site_dir)
