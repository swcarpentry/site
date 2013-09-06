"""
This is a minimal server to receive github's webhook on commit and fire a site
build.

To run this webhook - make sure the server has all build chain requirements for
the site.

Pull a clone of the site repo, then:

    pip install flask gunicorn netaddr

To run the webhook server, cd into the repo and then, this should be put in
the machines's startup config:

        gunicorn -b 0.0.0.0:9000 webhook:app -D
"""

from flask import Flask, request
import json
from netaddr import IPNetwork, IPAddress
from subprocess import call

app = Flask(__name__)


@app.route('/', methods=['POST'])
def update():
    # check that request is coming from github
    if (IPAddress(request.remote_addr) in IPNetwork("204.232.175.64/27") or
            IPAddress(request.remote_addr) in IPNetwork("192.30.252.0/22")):
        # TODO verify post data coming in for desired repo and master branch
        if 'payload' in request.form:
            data = json.loads(request.form['payload'])
            print data
            call('git pull && make install', shell=True)
        else:
            print "no data"
    else:
        print "invalid IP"

    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
