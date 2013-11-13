#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import argparse
import tempfile
import subprocess
import unicodedata
import glob
import os
import shutil

parser = argparse.ArgumentParser(description='Generate certificates.')
parser.add_argument('--svg', required=True,
                    help='Path to certificate SVG.')
parser.add_argument('--csv',
                    help='CSV file containing participant info.')

args = parser.parse_args()

if not args.csv:
    certificate_data = [{'name': 'Joe Doe', 'date': 'September 2013'},
                        {'name': 'Sarah Rowland', 'date': 'June 2012'},
                        {'name': 'Stéfan', 'date': '--'}]

basedir = os.path.join(os.path.dirname(__file__), './')
svg = open(args.svg).read()

tmp_dir = os.path.dirname(tempfile.NamedTemporaryFile().name)
for badge in glob.glob(basedir + '../img/badges/*.png'):
    shutil.copy(badge, tmp_dir)

for n, certificate in enumerate(certificate_data):
    this_svg = svg
    for key, value in certificate.items():
        this_svg = this_svg.replace('{{ %s }}' % key, value)

    tmp = tempfile.NamedTemporaryFile(suffix='.svg')
    tmp.write(this_svg)
    tmp.flush()

    filename = ('%03d_' % n) + certificate['name'].decode('utf-8') + '.pdf'
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore')
    filename = filename.replace(' ', '_')

    RED = '\033[1;37m'
    CLEAR = '\033[0m'
    print(RED + 'Exporting certificate', filename, CLEAR)

    subprocess.call(['inkscape',
                     '--export-pdf', filename,
                     tmp.name,
                     '--export-dpi', '600'])

