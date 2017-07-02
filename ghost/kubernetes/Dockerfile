FROM bprashanth/ghost:0.3

ADD themes /usr/src/ghost/content/themes
ADD config.js /usr/src/ghost/staging_config.js

# Set these options through the kubernetes yaml instead.
# i.e ues command or ENTRYPOINT, args for CMD, and containerPort for EXPOSE,
# that way people are fee to modify args to entrypoint/port etc.
# EXPOSE 2368
# ENTRYPOINT  ["/entrypoint.sh"]
# CMD ["npm", "start"]

