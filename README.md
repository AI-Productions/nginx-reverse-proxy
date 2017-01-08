# nginx-reverse-proxy
Quickly setup a nginx reverse proxy for http servers or websockets (ssl support eventually)

## Tested to work on

* Ubuntu 16.04

## Use

```
wget https://raw.githubusercontent.com/AI-Productions/nginx-reverse-proxy/master/nrp.py

sudo python3.6 nrp.py -r <a[ppend]/o[verwrite]> -p <port> -d <domain> -t <http/ws>
```
