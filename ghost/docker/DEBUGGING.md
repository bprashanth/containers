## Running on a fresh machine

```console
$ rm -rf $HOME/ghost

$ docker rm ghost; docker run -d --env NODE_ENV=development --name ghost -p 8080:2368 -v $HOME/ghost:/var/lib/ghost -v $(dirname `pwd`)/kubernetes/themes:/usr/src/ghost/content/themes -v $(dirname `pwd`)/kubernetes/config.js:/usr/src/ghost/config.js ghost:0.11.13

$ docker rm ghost; docker run -d --env NODE_ENV=development --name ghost -p 8080:2368 -v $HOME/ghost:/var/lib/ghost:Z -v $(dirname `pwd`)/kubernetes/themes:/usr/src/ghost/content/themes:Z -v $(dirname `pwd`)/kubernetes/config.js:/usr/src/ghost/config.js:Z bprashanth/ghost:0.5
```

Running on an existing machine just requires the second command, or a `docker restart ghost`

## Runtime command dumps from the remote vm

Login to digital ocean (0x1406F40@gmail.com)

```console
[root@inkdrop ~]# docker ps
CONTAINER ID        IMAGE                   COMMAND                  CREATED             STATUS              PORTS                    NAMES
549673897d0b        abiosoft/caddy:latest   "/bin/parent caddy..."   5 months ago        Up 5 months                                  caddy
c1c58b33313b        bprashanth/ghost:0.5    "/entrypoint.sh np..."   13 months ago       Up 5 months         0.0.0.0:8080->2368/tcp   ghost

[root@inkdrop ~]# docker ps --no-trunc
CONTAINER ID                                                       IMAGE                   COMMAND                                                                      CREATED             STATUS              PORTS                    NAMES
549673897d0be620cf4326216a9b3415215751c77e53731c6e607428b7eb7027   abiosoft/caddy:latest   "/bin/parent caddy --conf /etc/Caddyfile --log stdout --agree=$ACME_AGREE"   5 months ago        Up 5 months                                  caddy
c1c58b33313bd5594040b8d96d0d371918578fe548e1a341575c007fb37f2c53   bprashanth/ghost:0.5    "/entrypoint.sh npm start"                                                   13 months ago       Up 5 months         0.0.0.0:8080->2368/tcp   ghost
```


Docker commands: 
```console
$ docker run -d --env NODE_ENV=production --name ghost -p 8080:2368   -v $HOME/ghost:/var/lib/ghost:Z   -v $(dirname `pwd`)/kubernetes/themes:/usr/src/ghost/content/themes:Z   -v $(dirname `pwd`)/kubernetes/config.js:/usr/src/ghost/config.js:Z   bprashanth/ghost:0.5

$ docker run --name caddy     -v $(dirname `pwd`)/caddy/Caddyfile:/etc/Caddyfile:Z     -v $(dirname `pwd`)/caddy/.caddy:/root/.caddy:Z     -p 80:80 -p 443:443 -e ACME_AGREE=true --net=host -d     abiosoft/caddy:latest
```

* We're running the caddy container as `net=host` on ports 80 and 443, and the
  docker container is redirecting `2368` to `8080`. Port `8080` redirects to
  `notwelcome.in`.
* The data is in `/var/lib/ghost` in the container and `$HOME/ghost` on the vm. 
* The themes are in `kubernetes/themes:/usr/src/ghost/content/themes`
* The ghost config is from `kubernetes/config.js:/usr/src/ghost/config.js`
* The kubernetes directory is largely redundant

The idea is that you try a theme out locally, push it, pull it from the server,
and restart with that theme live. Currently available themes are 
```
[root@inkdrop ~]# ls src/github.com/bprashanth/containers/ghost/kubernetes/themes/
casper  coder  coder_dark  kaldorei
```

These will also show up under `General` settings in the admin 

## Debugging the docker image

Build a new container
First change the `Dockerfile` appropriately (eg to point to a new base image).

```
$ cd docker
$ docker build --tag bprashanth/ghost:0.6 .
$ docker run -it --entrypoint /bin/bash bprashanth/ghost:0.6
```

A docker inspect on a production build will show you the following mounts
```
"Mounts": [
    {
        "Type": "bind",
        "Source": "/root/src/github.com/bprashanth/containers/ghost/kubernetes/config.js",
        "Destination": "/usr/src/ghost/config.js",
        "Mode": "Z",
        "RW": true,
        "Propagation": "rprivate"
    },
    {
        "Type": "bind",
        "Source": "/root/src/github.com/bprashanth/containers/ghost/kubernetes/themes",
        "Destination": "/usr/src/ghost/content/themes",
        "Mode": "Z",
        "RW": true,
        "Propagation": "rprivate"
    },
    {
        "Type": "bind",
        "Source": "/root/ghost",
        "Destination": "/var/lib/ghost",
        "Mode": "Z",
        "RW": true,
        "Propagation": "rprivate"
    }
],

```

And the following env vars
```
"Env": [
    "NODE_ENV=production",
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "NODE_VERSION=6.14.2",
    "YARN_VERSION=1.6.0",
    "GOSU_VERSION=1.10",
    "GHOST_SOURCE=/usr/src/ghost",
    "GHOST_VERSION=0.11.13",
    "GHOST_CONTENT=/var/lib/ghost"
],

```


