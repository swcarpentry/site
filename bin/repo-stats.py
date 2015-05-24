__author__ = 'atlanmod'

import sys
import datetime
import requests
from cStringIO import StringIO
import gzip
import re
import json
import yaml

START_URL = 'http://data.githubarchive.org/'
END_URL = '.json.gz'

timeout_threshold = 5

OUTPUT_EVENT_FILE = '/tmp/swcarpenter.json'
OUTPUT_STATS_FILE = 'stats.yml'
OUTPUT_HTML_FILE = 'stats.html'

REPOSITORIES = [
    'swcarpentry/shell-novice',
    'swcarpentry/git-novice',
    'swcarpentry/hg-novice',
    'swcarpentry/sql-novice-survey',
    'swcarpentry/python-novice-inflammation',
    'swcarpentry/r-novice-inflammation',
    'swcarpentry/matlab-novice-inflammation',
    'swcarpentry/slideshows',
    'swcarpentry/instructor-training',
    'swcarpentry/amy',
    'swcarpentry/site'
]

EVENTS = [
    'IssueOpened',
    'IssueClosed',
    'IssueComment',
    'PullRequestOpened',
    'PullRequestClosed',
    'PullRequestComment'
]


def serialize_events(output_file, content):
    output_file.write(content + '\n')


def serialize_stats(stats):
    with open(OUTPUT_STATS_FILE, 'w+') as f:
        yaml.dump(stats, f, encoding='utf-8', allow_unicode=True)


def tablify_stats(stats):
    with open(OUTPUT_HTML_FILE, 'w') as f:
        print('<table class="table table-striped">', file=f)
        print('<tr><th>Project</th><th colspan="3">Issues</th><th colspan="3">Pull Requests</th></tr>', file=f)
        print('<tr><th></th><th>Opened</th><th>Closed</th><th>Comments</th><th>Opened</th><th>Closed</th><th>Comments</th></tr>', file=f)
        for r in REPOSITORIES:
            print('<tr><td>{0}</td>'.format(r.replace('swcarpentry/','')),, file=f)
            for e in EVENTS:
                val = stats.get(r, {e:''}).get(e, '')
                print('<td>{0}</td>'.format(val),, file=f)
            print('</tr>', file=f)
        print('</table>', file=f)

def get_githubarchive_format(date):
    d = datetime.datetime.strptime(date, "%Y-%m-%d-%H")
    output_format = re.sub(r'-[0-9][0-9]$', '', date)
    if d.hour == 00:
        output_format += '-0'
    else:
         output_format += '-' + str(d.hour).lstrip('0')

    return output_format


def get_data_from_date_to_date(starting_date, ending_date):
    #open file to store the repo information
    event_file = open(OUTPUT_EVENT_FILE, 'w+')

    #iterate over all github events between the starting day and today
    current_date = starting_date
    while current_date != ending_date:
        print('processing: {0}'.format(current_date))
        url = u'http://data.githubarchive.org/{0}.json.gz'.format(get_githubarchive_format(current_date))
        try:
            response = requests.get(url, timeout=timeout_threshold)
            results = gzip.GzipFile(fileobj=StringIO(response.content))
            data = results.read()
            for line in data.split('\n'):
                line_unicoded = unicode(line, errors='ignore')
                line_predecoded = re.sub(r'}{"(?!\W)', '}JSONDELIMITER{"', line_unicoded)
                for line_decoded in line_predecoded.split('JSONDELIMITER'):
                    if len(line_decoded) > 0:
                        try:
                            github_event = json.loads(line_decoded)
                            repository = github_event.get("repo")

                            if repository is not None:
                                name = repository.get("name")
                                #look for your repository events
                                if name in REPOSITORIES:
                                    #serialize the events into the event file
                                    serialize_events(event_file, line_decoded)
                            else:
                                sys.stderr.write(github_event)
                        except:
                            sys.stderr.write("JSON failed:" + line_decoded)
        except:
            sys.stderr.write(url + ' timeout exceeded, data not retrieved!')

        #update current date
        d = datetime.datetime.strptime(current_date, "%Y-%m-%d-%H")
        d = d + datetime.timedelta(hours=1)
        current_date = d.strftime("%Y-%m-%d-%H")

    #close file
    event_file.close()


def process_pullrequest(event):
    action = event.get('payload').get("action")
    if action == "opened" or action == "reopened":
        info = {'type': 'PullRequestOpened'}
    elif action == "closed":
       info = {'type': 'PullRequestClosed'}
    else:
        info = {'type': 'not_treated'}

    return info


def process_pullrequest_comment(event):
    action = event.get('payload').get('action')
    if action == "created":
        info = {'type': 'PullRequestComment'}
    else:
        info = {'type': 'not_treated'}

    return info


def process_issue(event):
    action = event.get('payload').get('action')
    if action == "opened" or action == "reopened":
        info = {'type': 'IssueOpened'}
    elif action == "closed":
        info = {'type': 'IssueClosed'}
    else:
        info = {'type': 'not_treated'}

    return info


def process_issue_comment(event):
    action = event.get('payload').get('action')
    if action == "created":
        info = {'type': 'IssueComment'}
    else:
        info = {'type': 'not_treated'}

    return info

#process a sub-set of github events (PullRequestEvent, PullRequestReviewCommentEvent, IssuesEvent, IssueCommentEvent)
#the rest are ignored
def process_event(event_type, event):
    if event_type == "PullRequestEvent":
        info = process_pullrequest(event)
    elif event_type == "PullRequestReviewCommentEvent":
        info = process_pullrequest_comment(event)
    elif event_type == "IssuesEvent":
        info = process_issue(event)
    elif event_type == "IssueCommentEvent":
        info = process_issue_comment(event)
    else:
        info = {'type': 'not_treated'}
        sys.stderr.write(event_type + " not treated!")

    return info


def update_stats(stats, repo, info):
    type = info.get('type')
    if type != 'not_treated':
        if stats.get(repo):
            repo_stats = stats.get(repo)
            if repo_stats.get(type):
                counter = repo_stats.get(type)
                repo_stats.update({type: counter+1})
            else:
                repo_stats.update({type: 1})
                stats.update({repo: repo_stats})
        else:
            repo_stats = {type: 1}
            stats.update({repo: repo_stats})
    return


def get_repo_stats():
    stats = {}
    event_file = open(OUTPUT_EVENT_FILE, 'r')
    for line in event_file:
        event = json.loads(line)
        event_type = event.get('type')
        repo_name = event.get('repo').get('name')
        info = process_event(event_type, event)
        update_stats(stats, repo_name, info)
    event_file.close()
    #serialize_stats(stats)
    tablify_stats(stats)
    return


def main():
    num_days = 7
    if len(sys.argv) > 1:
        num_days = int(sys.argv[1])
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=num_days)
    end_date = end_date.strftime("%Y-%m-%d-%H")
    start_date = start_date.strftime("%Y-%m-%d-%H")
    get_data_from_date_to_date(start_date, end_date)
    get_repo_stats()

if __name__ == "__main__":
    main()
