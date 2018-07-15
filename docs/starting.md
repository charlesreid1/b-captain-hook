# Starting Captain Hook

## Captain Hook Docker Pod

To run Captain Hook, we utilize a Docker compose file
to run the container that runs Captain Hook and mounts the
correct directories in the correct locations.

See [docker-compose.yml](https://github.com/charlesreid1/b-captain-hook/blob/master/docker-compose.yml)
in the Captain Hook repository.

## Startup Service: Captain Hook Docker Pod

In order to start the Captain Hook docker pod automatically
at startup, and automatically restart the pod if it crashes or
is stopped, we install a startup service called `dockerpod-captainhook`:

```
[Unit]
Description=captain hook webhook server docker pod
Requires=docker.service
After=docker.service

[Service]
Restart=always
ExecStart=/usr/local/bin/docker-compose -f /home/charles/codes/bots/b-captain-hook/docker-compose.yml up
ExecStop=/usr/local/bin/docker-compose  -f /home/charles/codes/bots/b-captain-hook/docker-compose.yml down

[Install]
WantedBy=default.target
```

This startup service runs `docker-compose` with the `-f` flag to specify
an absolute path to the Captain Hook `docker-compose.yml` file.

## Startup Service: Captain Hook Canary

Captain Hook listens for incoming web hooks and (optionally) runs a script in the `hooks/`
folder, based on the type of action, the name of the repository, and the
name of the branch.

However, there is one tricky task: Captain Hook must be able update _itself_
when there are changes pushed to the Captain Hook repository.

To resolve this, we run a "canary" startup service for Captain Hook.
This canary startup service runs a shell script that checks (every 10 seconds)
for the presence of a file at `/tmp/triggers/`.  If this file is present, the
host copy of Captain Hook is updated, the Captain Hook docker pod is restarted,
and the trigger file is removed.

This allows webhooks received by Captain Hook (which occur _inside_ of a Docker
container) to trigger an event on the host machine by bind-mounting
`/tmp/triggers/` and adding a file to this directory.

**`captain-hook-canary.service`:**

```
[Unit]
Description=captain hook canary script
Requires=dockerpod-captainhook.service
After=dockerpod-captainhook.service

[Service]
Restart=always
ExecStart=/home/charles/blackbeard_scripts/captain_hook_canary.sh
ExecStop=/usr/bin/pgrep -f captain_hook_canary | /usr/bin/xargs /bin/kill 

[Install]
WantedBy=default.target
```

Also see [captain-hook-canary.service](https://git.charlesreid1.com/dotfiles/debian/src/branch/master/services/captain-hook-canary.service)
in <https://git.charlesreid1.com/dotfiles/debian>.

This script calls the Captain Hook canary script, which is given below:

**`captain_hook_canary.sh`:**

```
#!/bin/bash

: '
Captain Hook Canary Script


Note: this needs an associated systemd service.
See the services directory of the dotfiles repo.

(snip comments)
'

while true
do
    # bootstrap-pull captain hook
    if [ -f "/tmp/triggers/push-b-captain-hook-master" ]; then
        echo "CAPTAIN HOOK'S CANARY:"
        echo "Running trigger to update Captain Hook on the host machine (user charles)"
        sudo -H -u charles python /home/charles/blackbeard_scripts/captain_hook_pull_host.py
        echo "All done."
        rm -f "/tmp/triggers/push-b-captain-hook-master"
    fi

    sleep 10;
done
```

Also see [captain_hook_canary.sh](https://git.charlesreid1.com/dotfiles/debian/src/branch/master/dotfiles/blackbeard_scripts/captain_hook_canary.sh)
in the `dotfiles/blackbeard_scripts` folder of
<https://git.charlesreid1.com/dotfiles/debian>.

When this canary script for Captain Hook is triggered by the presence of
a file at `/tmp/triggers/push-b-captain-hook-master` (which is mounted
inside the container at th same location as outside the container), it will
run a script to pull Captain Hook:

**`captain_hook_pull_host.py`:**

```
#!/usr/bin/env python3
import subprocess
import os
import time

"""
Captain Hook: Pull Captain Hook on the Host 

This script is called by the host machine 
(blackbeard) running the Captain Hook container.

This is triggered by push actions to the 
master branch of b-captain-hook.

The action is to update (git pull) the copy 
of captain hook running on the host, and
restart the container pod.
"""

work_dir = os.path.join('/home','charles','codes','bots','b-captain-hook')

# Step 1:
# Update Captain Hook
pull_cmd = ['git','pull','origin','master']
subprocess.call(pull_cmd, cwd=work_dir)

time.sleep(5)

# Step 2:
# Restart Captain Hook pod
pod_restart = ['docker-compose','restart']
subprocess.call(pod_restart, cwd=work_dir)

```




