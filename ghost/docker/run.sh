#!/bin/bash
docker run -d --env NODE_ENV=development --name ghost -p 80:2368 \
  -v $HOME/ghost:/var/lib/ghost \
  -v $(dirname `pwd`)/kubernetes/themes:/usr/src/ghost/content/themes \
  -v $(dirname `pwd`)/kubernetes/config.js:/usr/src/ghost/staging_config.js \
  bprashanth/ghost:0.3

