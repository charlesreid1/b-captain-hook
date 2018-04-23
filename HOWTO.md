# making a new site for a new container

## preparing materials to build site 

add mkdocs-material submodule:

```
git submodule add https://git.charlesreid1.com/charlesreid1/mkdocs-material
```

Copy an mkdocs config file into the folder:

```
cp /some/other/path/mkdocs.yml mkdocs.yml
```

Edit the config file and set the color/name:

```
vim mkdocs.yml
```

Make an index from the README:

```
cp README.md docs/index.md
```

Now we have all the materials ready to build the site.

## preparing place to put site

Clone a copy of the repo to `site`.

If there is no `gh-pages` branch, this clones it to `site` and creates an 
initial commit on the branch so it is ready to go:

```
git clone https://git.charlesreid1.com/org/repo site
cd site
git checkout --orphan gh-pages
rm -rf * .gitignore .gitmodules
echo '<h2>hello world</h2>' > index.html
git add -A .
git commit -a -m 'initial commit of gh-pages branch'
git push origin gh-pages
```

If there is a `gh-pages` branch:

```
git clone -b gh-pages https://git.charlesreid1.com/org/repo site
```

## preparing the infrastructure

need to add two things:

* webhook from gitea, to send a JSON payload when a commit is pushed (when the site is updated)
* hook script in captain hook, to deploy/update the site on pages.charlesreid1.com

To add the webhook:

* Open repo in Gitea
* Settings
* Webhooks
* Add Webhook (Gitea)
* Endpoint: https://hooks.charlesreid1.com/webhook
* Secret: (insert)
* Save webhook
* Test webhook

To add the hook script to captain hook:

* Add push-reponame-gh-pages to `hooks/` directory in Captain Hook repo
* Use others as template


## The Final Test

Check if everything is working

## debugging

Shell windows:

* Window on any machine to edit/commit/push to captain hook master branch (to trigger canary script)
* Window on blackbeard to `ls /tmp/triggers` and check if canary script is firing
* Window on blackbeard to `tail -f /var/log/syslog` and check for messages from canary script and pull script
* Window in captain hook container to `cat hooks/name-of-hook` and ensure hook script is being updated

(Make sure to give the canary service about 10 seconds to find the trigger file
and another 20 seconds to restart the Captain Hook container.)

