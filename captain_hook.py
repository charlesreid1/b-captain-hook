import os
import logging
import subprocess
from tempfile import mkstemp
from os import access, X_OK, remove, fdopen
import requests
import json
from flask import Flask, request, abort

app = Flask(__name__)


logging.basicConfig(filename='/tmp/captain_hook.log',
                    filemode='a',
                    level=logging.DEBUG)


@app.route('/webhook', methods=['GET', 'POST'])
def index():
    """
    Main WSGI application entry.
    """
    path = os.path.dirname(os.path.abspath(__file__))

    # Only POST is implemented
    if request.method != 'POST':
        logging.error('ERROR: Only POST method is implemented')
        abort(501)

    # Load config
    with open(os.path.join(path, 'config.json'), 'r') as cfg:
        config = json.loads(cfg.read())

    hooks_path = config.get('hooks_path', os.path.join(path, 'hooks'))
    logging.info("Hooks path: %s"%(hooks_path))

    # Implement ping/pong
    event = request.headers.get('X-GitHub-Event', 'ping')
    if event == 'ping':
        return json.dumps({'msg': 'pong'})

    # Gather data
    try:
        payload = request.get_json()

    except Exception:
        logging.warning('Request parsing failed')
        abort(400)

    # Enforce secret
    secret = config.get('enforce_secret', '')
    if secret!='':
        try:
            if payload['secret'] != secret:
                logging.error('Invalid secret %s.'%(payload['secret']))
                abort(403)
        except:
            abort(501)

    # Determining the branch is tricky, as it only appears for certain event
    # types an at different levels
    branch = None
    try:
        # Case 1: a ref_type indicates the type of ref.
        # This true for create and delete events.
        if 'ref_type' in payload:
            if payload['ref_type'] == 'branch':
                branch = payload['ref']

        # Case 2: a pull_request object is involved. This is pull_request and
        # pull_request_review_comment events.
        elif 'pull_request' in payload:
            # This is the TARGET branch for the pull-request, not the source
            # branch
            branch = payload['pull_request']['base']['ref']

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

    # Possible hooks
    hooks = []
    if branch and name:
        hooks.append(os.path.join(hooks_path, '{event}-{name}-{branch}'.format(**meta)))
    if name:
        hooks.append(os.path.join(hooks_path, '{event}-{name}'.format(**meta)))

    hooks.append(os.path.join(hooks_path, '{event}'.format(**meta)))
    hooks.append(os.path.join(hooks_path, 'all'))


    #######################################################
    # Check permissions
    scripts = []
    for h in hooks:
        if os.path.isfile(h) and access(h,X_OK):
            scripts.append(h)
    
    if len(scripts)==0:
        logging.warning('Scripts failed to execute')
        return json.dumps({'status': 'nop'})
    #######################################################

    # Save payload to temporal file
    osfd, tmpfile = mkstemp()
    with fdopen(osfd, 'w') as pf:
        pf.write(json.dumps(payload))

    # Run scripts
    logging.info("%s"%(scripts))
    ran = {}
    for s in scripts:

        proc = subprocess.Popen(
            [s, tmpfile, event],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()

        ran[os.path.basename(s)] = {
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
        return json.dumps({'status': 'done'})

    output = json.dumps(ran, sort_keys=True, indent=4)

    return output



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

