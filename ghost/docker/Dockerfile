FROM ghost:0.11.10

RUN apt-get update -y && apt-get install rsync vim sqlite3 -y
ADD entrypoint.sh /entrypoint.sh
EXPOSE 2368
WORKDIR /usr/src/ghost
ENTRYPOINT  ["/entrypoint.sh"]
CMD ["npm", "start"]

