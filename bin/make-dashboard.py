#!/usr/bin/env python

'''Create YAML for dashboard page by querying GitHub repositories.'''

import sys
import yaml
from github import Github
from optparse import OptionParser

CONTROLS = (
    ('swcarpentry/shell-novice', 'Introduction to the Unix shell'),
    ('swcarpentry/git-novice', 'Introduction to Git'),
    ('swcarpentry/hg-novice', 'Introduction to Mercurial'),
    ('swcarpentry/sql-novice-survey', 'Introduction to SQL'),
    ('swcarpentry/python-novice-inflammation', 'Python for non-programmers'),
    ('swcarpentry/r-novice-inflammation', 'R for non-programmers'),
    ('swcarpentry/matlab-novice-inflammation', 'MATLAB for non-programmers'),
    ('swcarpentry/slideshows', 'Software Carpentry presentations'),
    ('swcarpentry/capstone-novice-spreadsheet-biblio', 'From Excel to a database via Python'),
    ('swcarpentry/instructor-training', 'What instructors need to know'),
    ('swcarpentry/python-novice-turtles', 'Python for non-programmers using Turtles'),
    ('swcarpentry/amy', 'Workshop administration tool'),
    ('swcarpentry/site', 'Software Carpentry website'),
)

USAGE = '''Usage: make-dashboard.py -o outputfile [-t tokenfile | -u username -p password]
If no credentials are supplied, user is prompted for username and password.
To store credentials, create a file called git-token.txt that contains your GitHub API token
and put it in the root directory of the 'site' project.'''

# Command-line options.
parser = OptionParser()
parser.add_option('-o', '--output', dest='output', help='output directory')
parser.add_option('-t', '--tokenfile', dest='tokenfile', help='GitHub token file')
parser.add_option('-u', '--username', dest='username', help='GitHub username')
parser.add_option('-p', '--password', dest='password', help='GitHub password')
options, args = parser.parse_args()

assert not args, USAGE

if options.tokenfile is not None:
    assert options.username is None and options.password is None, USAGE
    with open(token_file, 'r') as reader:
        token = reader.read().strip()
        g = Github(token)

elif options.username is not None and options.password is not None:
    g = Github(options.username, options.password)

elif options.username is None and options.password is None:
    username = raw_input('username: ')
    password = raw_input('password: ')
    g = Github(username, password)

else:
    assert False, USAGE
    
# Process data.
all_records = []
dashboard = {
    'records' : all_records,
    'num_repos' : 0,
    'num_issues' : 0
}
for (ident, description) in CONTROLS:
    print '+', ident
    dashboard['num_repos'] += 1
    r = g.get_repo(ident)
    record = {'ident' : ident,
              'description' : description,
              'url' : str(r.html_url),
              'issues' : []}
    all_records.append(record)
    for i in r.get_issues(state='open'):
        record['issues'].append({'number' : i.number,
                                 'title' : str(i.title),
                                 'url' : str(i.html_url),
                                 'updated' : i.updated_at.strftime('%Y-%m-%d')})
        dashboard['num_issues'] += 1
    record['issues'].sort(lambda x, y: - cmp(x['updated'], y['updated']))

# Output.
with open(output_file, 'w') as writer:
    yaml.dump(dashboard, writer, encoding='utf-8', allow_unicode=True)
