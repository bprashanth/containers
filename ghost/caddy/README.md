# Caddy docker

Instructions for running a caddy server with the provided `CaddyFile`.

## Running 

`cd` into the docker directory
```
$ cd github.com/bprashanth/containers/ghost/docker

$ ls -lh ../
total 0
drwxr-xr-x. 3 root root 54 May 31 05:09 caddy
drwxr-xr-x. 2 root root 92 May 31 05:09 docker
drwxr-xr-x. 4 root root 91 May 28 08:37 kubernetes
```

and execute
```
$ docker run --name caddy \ 
    -v $(dirname `pwd`)/caddy/Caddyfile:/etc/Caddyfile:Z \
    -v $(dirname `pwd`)/caddy/.caddy:/root/.caddy:Z \
    -p 80:80 -p 443:443 -e ACME_AGREE=true --net=host -d \
    abiosoft/caddy:latest
```

NB: both `net=host` and `:latest` are anti-patterns. I feel like I must atleast mention this. This will spin up a caddy server listening on both `80` and `443`, and proxying all requests to `localhost:8080`. 
