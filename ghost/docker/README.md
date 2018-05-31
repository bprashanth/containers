# Ghost dockerfile

A clone of ghost that allows me to control the mount/entrypoints/themes/config.

## Running

`cd` into the directory this README is in

```
$ cd github.com/bprashanth/containers/ghost/docker
$ ls -lh
-rw-r----- 1 beeps eng  114 May  6 11:16 Dockerfile
-rw-r----- 1 beeps eng  430 May  6 11:15 entrypoint.sh
-rw-r----- 1 beeps eng  176 May  6 10:48 Makefile
-rw-r----- 1 beeps eng 1.6K May  6 11:38 README.md

$ ls -lh ../kubernetes
-rw-r----- 1 beeps eng 4.5K Jul  2 13:01 config.js
-rw-r----- 1 beeps eng  940 Jul  2 13:01 deployment.yaml
-rw-r----- 1 beeps eng  123 Jul  2 13:01 Dockerfile
drwxr-x--- 4 beeps eng 4.0K Jul  2 13:01 themes
```

and execute
```
$ docker run -d --env NODE_ENV=production --name ghost -p 8080:2368 \
  -v $HOME/ghost:/var/lib/ghost:Z \
  -v $(dirname `pwd`)/kubernetes/themes:/usr/src/ghost/content/themes:Z \
  -v $(dirname `pwd`)/kubernetes/config.js:/usr/src/ghost/config.js:Z \
  bprashanth/ghost:0.5
```

and visit `:8080`

## Modifying themes

* Clone someones theme from github into `/themes`, e.g the [coder theme](https://github.com/mbejda/CoderGhostTheme)
* run this image locally, hack on the theme
* git commit and push to your repo
* git pull in production and reload docker

## Directories

The default ghost image has 2 important directories:
* `GHOST_SOURCE`: node modules etc, defaults to `/usr/src/ghost`
* `GHOST_CONTENT`: the content of your blog, defaults to `/var/lib/ghost`

You might want to mont:
* config.js: for webserver config
* content: the content of your blog, mounted into `$GHOST_CONTENT`. Remember
  this directory is NOT checked into github, so backup that volume, or at least
  the sqlite database in `/var/lib/ghost/data/ghost.db` which is where all your
  production posts are stored.
* themes: the theme you've been hacking on, lives in `$GHOST_SOURCE` but is
  copied into `$GHOST_CONTENT` in `entrypoint.sh`.
