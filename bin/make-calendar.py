#!/usr/bin/env python3
'''
Compile the Software Carpentry calendar file.
'''

import sys
import os
import yaml
import datetime
import re
from optparse import OptionParser
try:  # Python 3
    from urllib.parse import urlparse
except ImportError:  # Python 2
    from urlparse import urlparse
from util import CONFIG_YML, STANDARD_YML, load_info

#----------------------------------------

def main():
    '''Main driver for calendar regeneration.'''

    options, args = parse_args()
    config = load_info(os.curdir)
    config['site'] = options.site
    calendar_file = os.path.join(options.output, 'workshops.ics')

    icw = ICalendarWriter()
    icw(calendar_file, config)

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

class ICalendarWriter(object):
    '''
    iCalendar generator for workshops.
    The format is defined in RFC 5545: http://tools.ietf.org/html/rfc5545
    '''

    def __call__(self, filename, config):
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Software Carpentry/Workshops//NONSGML v1.0//EN',
        ]
        for bc in config['workshops']:
            lines.extend(self.workshop(config['site'],
                                       config['timestamp'], bc))
        lines.extend(['END:VCALENDAR', ''])
        content = '\r\n'.join(lines)
        # From RFC 5545, section 3.1.4 (Character Set):
        # The default charset for an iCalendar stream is UTF-8.
        with open(filename, 'wb') as writer:
            writer.write(content.encode('utf-8'))

    def workshop(self, site, timestamp, info):
        uid = '{0}@{1}'.format(info['slug'],
                               urlparse(site).netloc or 'software-carpentry.org')
        if ('end' in info) and info['end']:
            end = info['end']
        else:  # one day workshop?
            end = info['start']
        end += datetime.timedelta(1)  # non-inclusive end date
        lines = [
            u'BEGIN:VEVENT',
            u'UID:{0}'.format(uid),
            u'DTSTAMP:{0}'.format(timestamp),
            u'DTSTART;VALUE=DATE:{:%Y%m%d}'.format(info['start']),
            u'DTEND;VALUE=DATE:{:%Y%m%d}'.format(end),
            u'SUMMARY:{0}'.format(self.escape(info['venue'])),
            u'DESCRIPTION;ALTREP="{0}":{0}'.format(info['url']),
            u'URL:{0}'.format(info['url']),
            u'LOCATION:{0}'.format(self.escape(info['venue'])),
        ]
        if info.get('latitude') and info.get('longitude'):
            latlng = '{0},{1}'.format(info['latitude'], info['longitude'])
            latlng = re.sub(r'\s+', '', latlng).replace(',', ';')
            lines.append('uGEO:{0}'.format(latlng))
        lines.append(u'END:VEVENT')
        return lines

    def escape(self, value):
        '''Escape text following RFC 5545.'''
        for char in ['\\', ';', ',']:
            value = value.replace(char, '\\' + char)
        value.replace('\n', '\\n')
        return value

#----------------------------------------

if __name__ == '__main__':
    main()
