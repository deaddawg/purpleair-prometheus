# purpleair-prometheus

## Purpose

Collect stats from Purple Air sensors on local network, and expose Prometheus metrics.

## Usage

```
usage: purple-prom.py [-h] [-d] [-p PORT] [-s SENSORS [SENSORS ...]]

Proxy purpleair local stats

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Verbose debug output
  -p PORT, --port PORT  Port to run webserver on [Default = 7884]
  -s SENSORS [SENSORS ...], --sensors SENSORS [SENSORS ...]
                        IP Address or hostname for PurpleAir on local network
```

For example,
```
$ python3 purple-prom.py -s 192.168.1.98 192.168.1.99
```

## Docker usage

```
docker run -it -e SENSORS="192.168.1.98 192.168.1.99" -e EXTRA_OPTS="-d" -p 7884:7884 deaddawg/purple-prom:latest
```
