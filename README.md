# b-captain-hook

Captain hook is a Python WSGI appication
taht handles webhooks from gitea
and github.

Forked from [carlos-jenkins/python-github-webhooks](https://github.com/carlos-jenkins/python-github-webhooks.git).

To install:

```
git clone https://github.com/carlos-jenkins/python-github-webhooks.git
cd python-github-webhooks
```

## Dependencies

Install dependencies with pip:

```
sudo pip install -r requirements.txt
```

## Setup

This requires a config file. See `config.json`.


`enforce_secret` - require `X-Hub-Signature` in header. Not enforced if empty.

`return_scripts_info` - return a JSON with the `stdout`, `stderr` and exit
code for each executed hook using the hook name as key. If this option is set
you will be able to see the result of your hooks from within your GitHub
hooks configuration page (see "Recent Deliveries").

`hooks_path` - Configures a path to import the hooks. `/hooks`


## Adding Hooks

This application will execute scripts in the hooks directory using the
following order:

(TODO: fix)

```
    hooks/{event}-{name}-{branch}
    hooks/{event}-{name}
    hooks/{event}
    hooks/all
```

The application will pass to the hooks the path to a JSON file holding the
payload for the request as first argument. The event type will be passed
as second argument. For example:

```
    hooks/push-myrepo-master /tmp/sXFHji push
```

Hooks can be written in any scripting language as long as the file is
executable and has a shebang. A simple example in Python could be:

```
    #!/usr/bin/env python
    # Python Example for Python GitHub Webhooks
    # File: push-myrepo-master

    import sys
    import json

    with open(sys.argv[1], 'r') as jsf:
      payload = json.loads(jsf.read())

    ### Do something with the payload
    name = payload['repository']['name']
    outfile = '/tmp/hook-{}.log'.format(name)

    with open(outfile, 'w') as f:
        f.write(json.dumps(payload))
```

Not all events have an associated branch, so a branch-specific hook cannot
fire for such events. For events that contain a `pull_request` object, the
base branch (target for the pull request) is used, not the head branch.

The payload structure depends on the event type. Please review:

```
    https://developer.github.com/v3/activity/events/types/
```


## Docker Deployment

`Dockerfile` defines the image, but use the `docker-compose.yml` file instead.

To build, start, and stop:

```
docker-compose build --no-cache
docker-compose up
docker-compose down
```

### Ports

This binds to external port 5000. 

Implementing a secret key is critical to keep 
captain hook from deploying random strangers' 
webhook requests.

In our case, the hook is reverse-proxied by nginx on krash,
so we know what IP to expect. 

(Problems implementing IP checking - 172 subrange, not 45 subrange.)

More important than validating the IP is validating the secret.


### Volumes

THe docker container mounts the `hooks/` directory
in this repository to `/hooks` in the container.

```
./hooks:/hooks
```

**NOTE: These scripts must be made executable with `chmod +x`
or the webhook server will not do anything and be totally silent.**

The docker container will also mount `/www/` into the container,
so all the static web content on the host (blackbeard) 
is available to the webhooks to perform updates and etc.

`/www` is mounted to the same place on the host and in the container:

```
/www:/www
```

### Testing

To test, you can trigger the webhook from the 
repository's webhooks panel.

Keep in mind this will _only_ fire triggers
on the master branch.


## Debugging

This container is an absolute pain in the ass to debug, 
and uses python 2 to boot. 

But it was the only thing working.

To test: 

* Run the server in one window
* In a second window, open a shell in the container and monitor `/tmp/*.log`
* In a third window, open a shell in the container and monitor `/www/*`

To open a shell in the container:

```
docker exec -it <name-of-container> /bin/sh
```

Remember you only have `/bin/sh` and `python2`,
no `bash` and no `python3`.

To check logs:

```
docker logs -f <container-name>
```

You can also run the container without sending it
to the background,

```
docker-compose up
```

and this will show exceptions on the screen
(but it won't show anything else useful...)


## License from Forked Repo

Copyright (C) 2014-2015 Carlos Jenkins <carlos@jenkins.co.cr>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.


## Credits

This project is just the reinterpretation and merge of two approaches:

[github-webhook-wrapper](https://github.com/datafolklabs/github-webhook-wrapper)

[flask-github-webhook](https://github.com/razius/flask-github-webhook)

