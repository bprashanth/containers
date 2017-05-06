#!/bin/bash
docker run -d --env NODE_ENV=production --name ghost -p 8080:2368 \
  -v $HOME/ghost:/var/lib/ghost \
  -v `pwd`/themes:/usr/src/ghost/content/themes \
  -v `pwd`/config.js:/usr/src/ghost/content/staging_config.js \
  bprashanth/ghost:0.2

