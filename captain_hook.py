# -*- coding: utf-8 -*-
#
# Copyright (C) 2014, 2015, 2016 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import logging
from sys import stderr, hexversion
logging.basicConfig(stream=stderr)

import hmac
from hashlib import sha1
from json import loads, dumps
from subprocess import Popen, PIPE
from tempfile import mkstemp
from os import access, X_OK, remove, fdopen
from os.path import isfile, abspath, normpath, dirname, join, basename

import requests
from ipaddress import ip_address, ip_network
from flask import Flask, request, abort


application = Flask(__name__)

logging.basicConfig(filename='/captain_hook.log',
                    filemode='a',
                    level=logging.DEBUG)

@application.route('/webhook', methods=['GET', 'POST'])
def index():
    """
    Main WSGI application entry.
    """
    path = normpath(abspath(dirname(__file__)))

    # Only POST is implemented
    if request.method != 'POST':
        abort(501)

    # Load config
    with open(join(path, 'config.json'), 'r') as cfg:
        config = loads(cfg.read())

    hooks = config.get('hooks_path', join(path, 'hooks'))

    # Allow whitelisted IPs only
    whitelist_ips = config.get('whitelist_ips', True)
    if whitelist_ips:
        if src_ip in ip_network('45.56.87.232'):
            break
        else:
            logging.error('IP {} not allowed'.format(
                src_ip
            ))
            abort(403)

    # Enforce secret
    secret = config.get('enforce_secret', '')
    if secret:
        try:
            if payload['secret'] != secret:
                logging.error('Invalid secret %s.'%(payload['secret']))
                abort(403)
        except:
            abort(501)

    # Implement ping
    event = request.headers.get('X-GitHub-Event', 'ping')
    if event == 'ping':
        return dumps({'msg': 'pong'})

    # Gather data
    try:
        payload = request.get_json()
    except Exception:
        logging.warning('Request parsing failed')
        abort(400)

    # Determining the branch is tricky, as it only appears for certain event
    # types an at different levels
    branch = None
    try:
        # Case 1: a ref_type indicates the type of ref.
        # This true for create and delete events.
        if 'ref_type' in payload:
            if payload['ref_type'] == 'branch':
                branch = payload['ref']

        ### # Case 2: a pull_request object is involved. This is pull_request and
        ### # pull_request_review_comment events.
        ### elif 'pull_request' in payload:
        ###     # This is the TARGET branch for the pull-request, not the source
        ###     # branch
        ###     branch = payload['pull_request']['base']['ref']

        elif event in ['push']:
            # Push events provide a full Git ref in 'ref' and not a 'ref_type'.
            branch = payload['ref'].split('/', 2)[2]

    except KeyError:
        # If the payload structure isn't what we expect, we'll live without
        # the branch name
        pass

    # All current events have a repository, but some legacy events do not,
    # so let's be safe
    name = payload['repository']['name'] if 'repository' in payload else None

    meta = {
        'name': name,
        'branch': branch,
        'event': event
    }
    logging.info('Metadata:\n{}'.format(dumps(meta)))

    ### # Skip push-delete
    ### if event == 'push' and payload['deleted']:
    ###     logging.info('Skipping push-delete event for {}'.format(dumps(meta)))
    ###     return dumps({'status': 'skipped'})

    # Possible hooks
    scripts = []
    if branch and name:
        scripts.append(join(hooks, '{event}-{name}-{branch}'.format(**meta)))
    if name:
        scripts.append(join(hooks, '{event}-{name}'.format(**meta)))
    scripts.append(join(hooks, '{event}'.format(**meta)))
    scripts.append(join(hooks, 'all'))


    #######################################################
    # Check permissions
    scripts = [s for s in scripts if isfile(s) and access(s, X_OK)]
    if not scripts:
        logging.warning('Scripts failed to execute')
        return dumps({'status': 'nop'})
    #######################################################

    # Save payload to temporal file
    osfd, tmpfile = mkstemp()
    with fdopen(osfd, 'w') as pf:
        pf.write(dumps(payload))

    # Run scripts
    logging.info("%s"%(scripts))
    ran = {}
    for s in scripts:

        proc = Popen(
            [s, tmpfile, event],
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = proc.communicate()

        ran[basename(s)] = {
            'returncode': proc.returncode,
            'stdout': stdout.decode('utf-8'),
            'stderr': stderr.decode('utf-8'),
        }

        # Log errors if a hook failed
        if proc.returncode != 0:
            logging.error('{} : {} \n{}'.format(
                s, proc.returncode, stderr
            ))

    # Clean up
    remove(tmpfile)

    info = config.get('return_scripts_info', False)
    if not info:
        return dumps({'status': 'done'})

    output = dumps(ran, sort_keys=True, indent=4)
    logging.info(output)
    return output


if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0')
