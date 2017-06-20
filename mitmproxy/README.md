# MITM the android emulator

Because why not?

## TLDR

setup a [forward proxy](#setting-up-a-forward-proxy), then run

```sh
$ android list avd
Available Android Virtual Devices:
    Name: 6P25large
  Device: Nexus 6P (Google)
    Path: /usr/local/home/beeps/.android/avd/Nexus_6P_API_25_large.avd
  Target: Google APIs (Google Inc.)
          Based on: Android 7.1.1 (Nougat) Tag/ABI: google_apis/x86
    Skin: nexus_6p
  Sdcard: /usr/local/home/beeps/.android/avd/Nexus_6P_API_25_large.avd/sdcard.img

$ emulator -avd 6P25large -http-proxy http://127.0.0.1:8080
```

Where the arguments to `-http-proxy` are the `hostname:port` the forward proxy is listening on. Push mitm proxy ca certs to the SD card so apps trust it
```
$ adb root
$ adb shell "mkdir -p /sdcard/ca/mitmproxy"
$ sudo adb push ~/.mitmrpoxy /sdcard/ca/mitmproxy
/usr/local/home/beeps/.mitmproxy/: 5 files pushed. 1.6 MB/s (6282 bytes in 0.004s)
```

install the cert through the emulator UI:
* `Settings` > `Security` > `Credential storage` > `Install from SD card`
* Pick your mitmproxy-ca-cert
* Enter your pin
* You should see a UI that asks for the name, and says "This package contains: on CA certificate" at the bottom
* `Settings` > `Security` > `Credential storage` > `User cerdentials` should show the new CA

## Setting up a forward proxy

Decrypt, log, re-encrypt, profi~~t~~le

## Nginx

My first thought was to reach for nginx

```nginx
worker_processes 4;
pid /run/nginx.pid;

events {
  worker_connections 768;
  multi_accept on;
}

http {
  server {
    resolver 8.8.8.8;
    listen  8080;
    large_client_header_buffers 4 16k;

    location / {
        proxy_pass              $scheme://$host$request_uri;
        proxy_set_header        Host $http_host;
        proxy_set_header        X-Real-IP       $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_ignore_headers "Set-Cookie";
    }
  }
}
```

Simple, but doesn't handle HTTP tunneled over `CONNECT`. Surprised face. Guess it isn't a replacement for squid after all.

## MITMProxy

Dead simple to setup and doesn't require learning `squid` DSL.
```sh
docker run --rm -itP -v /tmp/logdir:/tmp/logdir -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy -p 8080:8080 mitmproxy/mitmproxy mitmproxy -v --host -w /tmp/logdir/dump.log
```

Will show you the ncurses UI and save a traffic dump you can analyze through the [python API](https://github.com/mitmproxy/mitmproxy/blob/2.0.x/examples/simple/filter_flows.py), the [processor script](processor.py) script in this directory does just that. Eg:
```
$ docker run --rm -itP -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy -v /tmp/logdir:/tmp/logdir -v ./processor.py:/tmp/processor.py mitmproxy/mitmproxy mitmdump -q --host -s "/tmp/processor.py google" -r dump.log
```

Remove `-q` if you just want matching flows annotated in the context of the entire dump. You can also start it up with filters:
```
$ docker run --rm -itP -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy -p 8080:8080  mitmproxy/mitmproxy mitmdump --ignore='^(?!sandbox\.google\.com)'
```

which ignores all hosts but `sandbox.google.com`
```
$ https_proxy=http://localhost:8080/ curl https://google.com -k
172.17.0.1:56158: clientconnect
172.17.0.1:56158: clientdisconnect

$ https_proxy=localhost:8080 curl https://sandbox.google.com -k
172.17.0.1:56186: GET https://sandbox.google.com/
               << 404 Not Found 49b
```

Note that mitmproxy sticks the ca-certs it uses to intercept HTTPS in ~/.mitmproxy.

