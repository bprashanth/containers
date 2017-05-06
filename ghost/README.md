# Ghost dockerfile

A clone of ghost that allows me to control the mount/entrypoints/themes/config.

## Running

`cd` into the directory this README is in

```
$ cd github.com/bprashanth/dockerfiles/ghost
$ ls -lh
-rw-r----- 1 beeps eng 4.6K May  6 11:19 config.js
-rw-r----- 1 beeps eng  114 May  6 11:16 Dockerfile
-rw-r----- 1 beeps eng  430 May  6 11:15 entrypoint.sh
-rw-r----- 1 beeps eng  176 May  6 10:48 Makefile
-rw-r----- 1 beeps eng 1.6K May  6 11:38 README.md
drwxr-x--- 2 beeps eng 4.0K May  6 11:44 themes
```

and execute
```
$ docker run -d --env NODE_ENV=production --name ghost -p 8080:2368 \
  -v $HOME/ghost:/var/lib/ghost \
  -v `pwd`/themes:/usr/src/ghost/content/themes \
  -v `pwd`/config.js:/usr/src/ghost/content/staging_config.js \
  bprashanth/ghost:0.1
```

and visit `:8080`

## Modifying themes

* Clone someones theme from github into `/themes`, i.e
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
