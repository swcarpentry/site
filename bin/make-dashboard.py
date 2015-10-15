#!/usr/bin/env python3

'''Create YAML for dashboard page by querying GitHub repositories.'''

import sys
import yaml
from util import DASHBOARD_CACHE

CONTROLS = (
    ('swcarpentry/shell-novice', 'Unix Shell'),
    ('swcarpentry/git-novice', 'Git'),
    ('swcarpentry/hg-novice', 'Mercurial'),
    ('swcarpentry/sql-novice-survey', 'SQL'),
    ('swcarpentry/python-novice-inflammation', 'Python'),
    ('swcarpentry/r-novice-inflammation', 'R'),
    ('swcarpentry/matlab-novice-inflammation', 'MATLAB'),
    ('swcarpentry/make-novice', 'Make'),
    ('swcarpentry/capstone-novice-spreadsheet-biblio', 'From Excel to a database via Python'),
    ('DamienIrving/capstone-oceanography', 'Data Management in the Ocean, Weather and Climate Sciences'),
    ('swcarpentry/matlab-novice-capstone-biomed', 'Controlling a Quadcoptor With Your Mind'),
    ('swcarpentry/web-data-python', 'Working With Data on the Web'),
    ('swcarpentry/amy', 'Workshop administration tool'),
    ('swcarpentry/site', 'Software Carpentry website'),
)

def get_connection(token_file):
    '''Get a connection to GitHub if the library and token file are available.'''
    try:
        from github import Github
        with open(token_file, 'r') as reader:
            token = reader.read().strip()
        cnx = Github(token)
    except:
        cnx = None
    return cnx

def process(cnx):
    '''Gather information.'''
    if not cnx:
        return []
    all_records = []
    dashboard = {
        'records' : all_records,
        'num_repos' : 0,
        'num_issues' : 0
    }
    for (ident, description) in CONTROLS:
        print('+', ident)
        dashboard['num_repos'] += 1
        r = cnx.get_repo(ident)
        record = {'ident' : ident,
                  'description' : description,
                  'url' : str(r.html_url),
                  'issues' : []}
        all_records.append(record)
        for i in r.get_issues(state='open'):
            try:
                record['issues'].append({'number' : i.number,
                                         'title' : str(i.title),
                                         'url' : str(i.html_url),
                                         'updated' : i.updated_at.strftime('%Y-%m-%d')})
            except Exception as e:
                print('failed with', i.number, i.title, i.html_url, i.updated_at, file=sys.stderr)
            dashboard['num_issues'] += 1
        record['issues'].sort(key=lambda x: x['updated'])
    return dashboard

def main():
    '''Main driver.'''
    token_file = sys.argv[1]
    output_file = sys.argv[2]
    cnx = get_connection(token_file)
    dashboard = process(cnx)
    with open(output_file, 'w') as writer:
        yaml.dump(dashboard, writer, encoding='utf-8', allow_unicode=True)

if __name__ == '__main__':
    main()
