import argparse
import logging
import requests
import sys
import time

from requests.exceptions import RequestException

from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server


DEFAULT_PORT = 7884
LOG = logging.getLogger(__name__)


class PurpleAirCollector:
    STATS_TO_COLLECT = [
        "current_temp_f",
        "current_humidity",
        "current_dewpoint_f",
        "pressure",
        "pm2.5_aqi",
        "p_10_0_um",
        "p_5_0_um",
        "p_2_5_um",
        "p_1_0_um",
        "p_0_5_um",
        "p_0_3_um",
        "pm10_0_cf_1",
        "pm2_5_cf_1",
        "pm1_0_cf_1",
        "pm10_0_atm",
        "pm2_5_atm",
        "pm1_0_atm"]
    KEY_PREFIX = "purpleair"
    LABELS = ["sensor_id", "module"]


    def __init__(self, sensors):
        self.sensors = sensors

    def _parse_results(self, raw_data, g, stat):
        for sensor, resp in raw_data.items():
             sensor_id = resp.get("SensorId")
             a = resp.get(stat)
             if a is not None:
                 g.add_metric([sensor_id, "a"], a)
             b = resp.get(f"{stat}_b")
             if b is not None:
                 g.add_metric([sensor_id, "b"], b)

    def _build_metrics(self, raw_data):
        for stat in self.STATS_TO_COLLECT:
            key = f"{self.KEY_PREFIX}_{stat}"
            key = key.replace(".", "_")
            desc = f"Gauge for {stat}"
            g = GaugeMetricFamily(key, desc, labels=self.LABELS)
            self._parse_results(raw_data, g, stat)
            yield g
            
    def collect(self):
        LOG.debug("Request to collect started")

        raw_data = {}
        for sensor in self.sensors:
            url = f"http://{sensor}/json"
            try:
                resp = requests.get(url=url)
            except RequestException as e:
                LOG.error(f"Could not connect to {sensor}, skipping")
                LOG.debug(f"Connection error: {e}")
                # reset data for sensor so prometheus does not collect stale data
                raw_data.pop(sensor, None)
                continue
            LOG.info(f"Collected from {url}")
            parsed_resp = resp.json()
            raw_data[sensor] = parsed_resp

        LOG.debug("Collection complete")
        return self._build_metrics(raw_data) 


def _handle_debug(debug):
    """Turn on debugging if asked otherwise INFO default"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Proxy purpleair local stats"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Verbose debug output"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to run webserver on [Default = {DEFAULT_PORT}]",
    )
    parser.add_argument(
        "-s",
        "--sensors",
        type=str,
        nargs="+",
        help="IP Address or hostname for PurpleAir on local network",
    )
    args = parser.parse_args()
    _handle_debug(args.debug)

    LOG.info(f"Starting {sys.argv[0]} on port {args.port}")
    start_http_server(args.port)
    REGISTRY.register(PurpleAirCollector(args.sensors))
    LOG.info(f"purpleair prometheus exporter - listening on {args.port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("Shutting down ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
