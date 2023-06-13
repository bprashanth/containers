FROM python:3.11.2-slim-buster
RUN apt update && \
      apt install -y curl && \
      apt install -y jq && \
      apt install -y vim && \
      curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
      chmod +x ./kubectl && \
      mv ./kubectl /usr/local/bin/kubectl
ADD allowed_ips.py /usr/local/bin/allowed_ips.py
ENTRYPOINT /usr/local/bin/allowed_ips.py
