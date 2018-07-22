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

