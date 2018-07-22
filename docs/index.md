# b-captain-hook

Captain hook is a Python WSGI appication that handles webhooks from gitea and
github.

Forked from [carlos-jenkins/python-github-webhooks](https://github.com/carlos-jenkins/python-github-webhooks.git).

To install captain hook:

```
git clone https://git.charlesreid1.com/bots/b-captain-hook.git
cd b-captain-hook
pip install -r requirements.txt
```

Now run it:

```
python captain_hook.py
```


## What is Captain Hook?

Captain Hook is a flask webhook server that runs via docker.

See [What is Captain Hook?](what.md) for an explanation.

## Configuring Captain Hook

Captain Hook requires a config file. See `config.example.json` in this 
directory, and the [Captain Hook Config](config.md) page.

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
branch. Then the webhook sent to Captain Hook would contain this
information, and Captain Hook would only look for the following
scripts, and run them if present:

```
b-captain-hook/
        hooks/push-happy-giraffe-gh-pages
        hooks/push-happy-giraffe
        hooks/push
        hooks/all
```

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


## Licenses

Original license (Charles Reid) and forked license
(Carlos Jenkins) given in [license.md](license.md)

## Credits

This project is just the reinterpretation and merge of two approaches:

[github-webhook-wrapper](https://github.com/datafolklabs/github-webhook-wrapper)

[flask-github-webhook](https://github.com/razius/flask-github-webhook)

It is implemented with the help of python 3 alpine:

[nikos/python3-alpine-flask-docker](https://github.com/nikos/python3-alpine-flask-docker)


