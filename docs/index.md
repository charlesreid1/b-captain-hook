# b-captain-hook

Captain hook is a Python WSGI appication that handles webhooks from gitea and
github.

Forked from [carlos-jenkins/python-github-webhooks](https://github.com/carlos-jenkins/python-github-webhooks.git).

To install captain hook:

```
git clone https://git.charlesreid1.com/bots/b-captain-hook.git
cd b-captain-hook
```

## Dependencies

Install dependencies with pip:

```
pip install -r requirements.txt
```

<br />
<br />

## What is Captain Hook?

### The Short Version

Captain Hook enables a Github Pages-like push-to-deploy setup for git.charlesreid1.com.

Installing webhooks into repositories on <https://git.charlesreid1.com>
allows the `gh-pages` branch of the given repository to be hosted live on
<https://pages.charlesreid1.com>.

### The Long Version

Captain Hook is a Python Flask server that listens for incoming web hooks from
Gitea (or Github), and uses those web hooks to deply pages to <https://pages.charlesreid1.com>.

Captain Hook works by providing a webhook endpoint (rounting provided by nginx
container in [pod-charlesreid1](https://git.charlesreid1.com/docker/pod-charlesreid))
that can be used to link a Gitea (or Github) repository to Captain Hook.

Gitea (and Github) send payloads with webhooks that specify information like the
action that triggered the webhook, and the repository/branch on which the
action was performed.

Captain Hook runs inside of a docker container. The docker container mounts the
pages.charlesreid1.com web directory inside the container. Generally the hook
scripts will deploy the `gh-apges` branch to this web directory.

## Starting Captain Hook

See [Starting Captain Hook](starting.md) for how to set up the various startup services
and docker pods that are required to run Captain Hook.


<br />
<br />

## Adding Hooks

Captain Hook will accept any incoming web hook that reaches it,
bt it will only run scripts if the event, repository name, and/or
branch to which changes were made matches the name of a script.

To add a new script to be triggered on a particular web hook:

```
    hooks/{event}-{name}-{branch}
    hooks/{event}-{name}
    hooks/{event}
    hooks/all
```


For example, suppose I performed a `push` action to a repository
named `happy-giraffe`, and I was pushing commits to the `gh-pages`
branch. Then the webhook sent to Captain Hook would contain this
information, and Captain Hook would only run relevant scripts:
(in this case, `hooks/{event}-{name}-{branch}`).

The application passes the path to a JSON file, while holding the payload
for the request as the first argument. Suppose we had an event where someone
pushed to the `happy-giraffe` repository, to the `gh-pages` branch. 

The application will pass in two pieces of information:

* Path to JSON file holding payload - the first part of the request
  is a JSON file that holds the payload for the request.
  
* The other piece of information passed is the name of the action
    (e.g., `push`)

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





# =======================================


This requires a config file. See `config.json`.


`enforce_secret` - require `X-Hub-Signature` in header. Not enforced if empty.

`return_scripts_info` - return a JSON with the `stdout`, `stderr` and exit
code for each executed hook using the hook name as key. If this option is set
you will be able to see the result of your hooks from within your GitHub
hooks configuration page (see "Recent Deliveries").

`hooks_path` - Configures a path to import the hooks. Example: `/app/hooks`


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
in this repository to `/app/hooks` in the container.

```
./hooks:/app/hooks
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


## License for Fork 

```plain
Copyright (c) 2018 Charles Reid

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## License from Forked Repo

```plain
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
```


## Credits

This project is just the reinterpretation and merge of two approaches:

[github-webhook-wrapper](https://github.com/datafolklabs/github-webhook-wrapper)

[flask-github-webhook](https://github.com/razius/flask-github-webhook)

it is implemented with the help of python 3 alpine:

[nikos/python3-alpine-flask-docker](https://github.com/nikos/python3-alpine-flask-docker)


# More Deets

Self-updating hooks: create mounted, shared directory
and create a canary watcher on the host.

Push events from container to host via presence of file,
container takes action and removes file.

