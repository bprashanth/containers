#!/bin/bash
set -e

if [ -f "${GHOST_SOURCE}/staging_config.js" ]; then
  # simply mounting it also does the trick but changes permissions on the host
  cp "${GHOST_SOURCE}/staging_config.js" "${GHOST_CONTENT}/config.js"
fi
mkdir -p "${GHOST_CONTENT}/content/themes"
chmod -cR 777 "${GHOST_SOURCE}/content/themes"
rsync -aI "${GHOST_SOURCE}/content/themes/" "${GHOST_CONTENT}/content/themes/"
chown -R user:user "$GHOST_CONTENT"
exec "$@"
