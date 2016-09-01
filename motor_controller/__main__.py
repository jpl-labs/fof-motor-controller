"""Main module to control the fan motors in the fans of fury game."""

import sys
import signal
import configparser
import logging

from .fans_of_fury import FansOfFury
from .pi_header import PiHeader
from .pin_mode import PinMode

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

logging.basicConfig(level=logging.DEBUG)


fans_of_fury = None


def sigterm_handler(signum, frame):
    logging.info('GAME: received sigterm')
    fans_of_fury.stop()
    sys.exit()

signal.signal(signal.SIGTERM, sigterm_handler)


if __name__ == "__main__":
    with PiHeader(mode=PinMode.BCM) as header:
        fans_of_fury = FansOfFury(CONFIG, header)
        fans_of_fury.run()
        
