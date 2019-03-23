# b-captain-hook

Captain hook is a Python WSGI application that handles webhooks from gitea and
github.

Forked from [carlos-jenkins/python-github-webhooks](https://github.com/carlos-jenkins/python-github-webhooks.git).

To install captain hook:

```
git clone https://git.charlesreid1.com/bots/b-captain-hook.git
cd b-captain-hook
pip install -r requirements.txt
cp config.example.json config.json
# edit config.json
```

Run it standalone:

```
python captain_hook.py
```

Run it with docker:

```
docker-compose build
docker-compose up -d
docker-compose down
```


## What is Captain Hook?

Captain Hook is a flask webhook server that runs via docker.

See [What is Captain Hook?](what.md) for an explanation.

## Configuring Captain Hook

Captain Hook requires a config file. See `config.example.json` in this 
directory, and the [Captain Hook Config](config.md) page for more info.

## Starting Captain Hook

See [Starting Captain Hook](starting.md) for how to set up the various startup services
and docker pods that are required to run Captain Hook.


## Adding Hooks

Captain Hook accepts incoming webhooks and checks for scripts in `hooks/`
that match the action performed on the given repository.

A webhook script is anything that is executable.

To add a new script to be triggered on a particular webhook,
put it in the `hooks/` directory and follow the naming convention:

```
b-captain-hook/
        hooks/{event}-{name}-{branch}
        hooks/{event}-{name}
        hooks/{event}
        hooks/all
```


For example, suppose I performed a `push` action to a repository
named `happy-giraffe`, and I was pushing commits to the `gh-pages`
branch. The webhook sent to Captain Hook would contain this
information, and Captain Hook would look for any webhooks with the
following names, and run them if present:

```
b-captain-hook/
        hooks/push-happy-giraffe-gh-pages
        hooks/push-happy-giraffe
        hooks/push
        hooks/all
```

The application passes the path to a JSON file, while holding the payload
for the request as the first argument. 

The application will pass in two pieces of information:

* Path to JSON file holding payload - the first part of the request
  is a JSON file that holds the payload for the request.
  
* The other piece of information passed is the name of the action
    (e.g., `push`)

The application will pass to the hooks the path to a JSON file holding the
payload for the request as first argument. The event type will be passed
as second argument. For example:

```
    hooks/push-happy-giraffe-master /tmp/sXFHji push
```

Hooks can be written in any scripting language as long as the file is
executable and has a shebang. A simple example in Python could be:

```
    #!/usr/bin/env python
    # Python Example for Python GitHub Webhooks
    # File: push-happy-giraffe-master

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

### Base Docker Image

Captain Hook uses the `python3-alpine-flask` container,
which is a very lightweight container with python 3 
available and with flask installed.

See [nikos/python3-alpine-flask-docker](https://github.com/nikos/python3-alpine-flask-docker)
on Github.

### Ports

Captain Hook binds to external port 5000 on 
whatever host it runs on.

Implementing a secret key is critical to keep 
captain hook from deploying webhook requests
from random strangers.

**Recommendations:** You can implement validation of the
IP address sending the webhook, but more important than 
validating the incoming IP address (which can always be
spoofed) is to validate the secret. 

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

`/www` is mounted to the same place on the host and in the container,
as indicated by this bind mount lin from the docker-compose file:

```
/www:/www
```

### Testing

To test Captain Hook, install a webhook in a given
repository and use the server running Captain Hook
as the endpoint. Set up the secret.

You should be able to trigger a webhook test from the 
repository's webhooks control panel. This should trigger
Captain Hook, and if you've added a script for the 
corresponding repository, it should be triggered by the test.

Keep in mind that Gitea/Github will _only_ fire triggers
on the master branch of a repository, so you can't test
arbitrary branches using this method.


## Debugging

To get into test/debug mode:

* Set up a "dummy" hook (the Python hook shown above) that will just log the webhook to a log file in `/tmp`
* Run the server in one window
* In a second window, open a shell in the container and monitor `/tmp/*.log`
* In a third window, open a shell in the container and monitor `/www/*`

To open a shell inside the container, run this command 
from the host machine:

```
docker exec -it <name-of-container> /bin/sh
```

Remember that when you are inside this container, you will only have
`/bin/sh` available - no `bash`.

To check logs of this container, run this from the host machine:

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


## Licenses

Original license (Carlos Jenkins) and forked license
(Charles Reid) given in [license.md](license.md)


## Credits

This project is just the reinterpretation and merge of two approaches:

[github-webhook-wrapper](https://github.com/datafolklabs/github-webhook-wrapper)

[flask-github-webhook](https://github.com/razius/flask-github-webhook)

It is implemented with the help of python 3 alpine:

[nikos/python3-alpine-flask-docker](https://github.com/nikos/python3-alpine-flask-docker)


