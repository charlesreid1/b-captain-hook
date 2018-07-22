## Captain Hook Config

Config file `config.json` should contain:

```
{
    "whitelist_ips": true,
    "enforce_secret": "SOMELONGSECRETSTRINGTHATYOUPASTEINTOGITHUBORGITEAWEBINTERFACE",
    "return_scripts_info": true,
    "hooks_path": "/hooks"
}
```

`enforce_secret` - require `X-Hub-Signature` in header. Not enforced if empty.

`return_scripts_info` - return a JSON with the `stdout`, `stderr` and exit
code for each executed hook using the hook name as key. If this option is set
you will be able to see the result of your hooks from within your GitHub
hooks configuration page (see "Recent Deliveries").

`hooks_path` - Configures a path to import the hooks. Example: `/app/hooks`

