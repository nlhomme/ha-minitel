"""Entry point for ha-minitel."""

import argparse
import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ha_minitel.config import Config
from ha_minitel.app import Application


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="ha-minitel: Minitel interface for Home Assistant")
    parser.add_argument("--language", default="fr", choices=["fr", "en"])
    parser.add_argument("--websocket-port", type=int, default=3615)
    parser.add_argument("--serial-device", default="")
    parser.add_argument("--serial-baud-rate", type=int, default=1200, choices=[1200, 4800, 9600])
    parser.add_argument("--serial-parity", default="even", choices=["none", "even", "odd"])
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    parser.add_argument("--ssl-certfile", default="")
    parser.add_argument("--ssl-keyfile", default="")
    args = parser.parse_args()

    return Config(
        language=args.language,
        websocket_port=args.websocket_port,
        serial_device=args.serial_device,
        serial_baud_rate=args.serial_baud_rate,
        serial_parity=args.serial_parity,
        log_level=args.log_level,
        ssl_certfile=args.ssl_certfile,
        ssl_keyfile=args.ssl_keyfile,
        ha_token=os.environ.get("SUPERVISOR_TOKEN", ""),
    )


def main():
    config = parse_args()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app = Application(config)
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
