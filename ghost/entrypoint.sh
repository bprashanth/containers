#!/bin/bash
set -e

mkdir -p "${GHOST_CONTENT}/content/themes"
# simply mounting it also does the trick but changes permissions on the host
cp "${GHOST_SOURCE}/staging_config.js" "${GHOST_CONTENT}/config.js"
rsync -aI "${GHOST_SOURCE}/content/themes/" "${GHOST_CONTENT}/content/themes/"
chown -R user:user "$GHOST_CONTENT"
exec "$@"
