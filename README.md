# b-captain-hook

Captain hook is a Python WSGI application that handles webhooks from gitea and
github.

Captain Hook documentation: <https://pages.charlesreid1.com/b-captain-hook>

Browse the documentation locally: [docs/index.md](docs/index.md)

Captain Hook source code: <https://git.charlesreid1.com/bots/b-captain-hook>

Captain Hook on Github: <https://github.com/charlesreid1-docker/captain-hook>

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

## Licenses

See [LICENSE](LICENSE)

## Credits

This project is just the reinterpretation and merge of two approaches:

[github-webhook-wrapper](https://github.com/datafolklabs/github-webhook-wrapper)

[flask-github-webhook](https://github.com/razius/flask-github-webhook)

It is implemented with the help of python 3 alpine:

[nikos/python3-alpine-flask-docker](https://github.com/nikos/python3-alpine-flask-docker)


