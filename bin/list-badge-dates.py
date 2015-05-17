import sys
import json

USAGE = 'Usage: {0} [--start date] filenames...'.format(sys.argv[0])

filenames = sys.argv[1:]
if not filenames:
    print(USAGE, file=sys.stderr)
    sys.exit(1)

start = None
if filenames[0] == '--start':
    if len(filenames) <= 1:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    start = filenames[1]
    filenames = filenames[2:]

for f in filenames:
    with open(f, 'r') as reader:
        data = json.load(reader)
        if 'issuedOn' in data:
            if (start is None) or (data['issuedOn'] >= start):
                print('{0}: {1}'.format(f, data['issuedOn']))
        else:
            print('No issuedOn in "{0}"'.format(f), file=sys.stderr)
