#!/bin/bash
set -e

mkdir -p "${GHOST_CONTENT}/content/themes"
cp "${GHOST_SOURCE}/config.js" "${GHOST_CONTENT}/config.js"
rsync -aI "${GHOST_SOURCE}/content/themes/" "${GHOST_CONTENT}/content/themes/"
chown -R user:user "$GHOST_CONTENT"
exec "$@"
