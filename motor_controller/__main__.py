"""Main module to control the fan motors in the fans of fury game."""

import sys
import signal
import configparser
import logging
import json

import asyncio
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

from .fan_device import FanDevice
from .fan_speed_change_event import FanSpeedChangeEvent
from .fans_of_fury import FansOfFury
from .device_controller_registration_event import DeviceControllerRegistrationEvent
from .logging_handler import LoggingHandler
from .pi_header import PiHeader
from .pin_mode import PinMode

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

logging.basicConfig(level=logging.INFO)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    def sigterm_handler(signum, frame):
        logging.info('GAME: received sigterm %s %s', signum, frame)
        loop.close()
        sys.exit()

    signal.signal(signal.SIGTERM, sigterm_handler)

    with PiHeader(mode=PinMode.BCM) as header:

        class Socket(LoggingHandler, WebSocketClientProtocol):

            def __init__(self):
                super(Socket, self).__init__()
                self.fof = None

            def onOpen(self):
                self.logger.info('Socket opened')

                self.fof = FansOfFury(CONFIG, header)

                # Register this device controller and its devices
                registration_message = DeviceControllerRegistrationEvent(
                    self.fof.device_controller_config)

                payload = json.dumps(registration_message, default=lambda o: o.__dict__,
                                     sort_keys=True, ensure_ascii=False).encode('utf8')

                self.logger.debug(
                    'Sending message through socket: %s', payload)
                self.sendMessage(payload, isBinary=False)
                self.logger.info('Sent registration message to server')

            def onMessage(self, payload, isBinary):
                self.logger.debug('Got message')
                if not isBinary:
                    self.logger.debug('Received message:  %s', payload)
                    dic = json.loads(payload.decode('utf8'))
                    dic['device'] = FanDevice(**dic['device'])
                    fan_speed_change_event = FanSpeedChangeEvent(**dic)
                    fan_id = int(fan_speed_change_event.device.id)
                    new_value = float(fan_speed_change_event.newSpeed)
                    self.logger.info(
                        'Received instruction to set fan %s to speed %s', fan_id, new_value)
                    self.fof.PLAY_SIDES[fan_id].motor.desired_speed = new_value

            def onClose(self, wasClean, code, reason):
                if reason:
                    self.logger.warn(reason)
                loop.stop()

        factory = WebSocketClientFactory(
            u'ws://192.168.31.99:8080/ws/fancontroller/websocket')
        factory.protocol = Socket

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, '192.168.31.99', 8080)
        loop.run_until_complete(coro)
        loop.run_forever()

    loop.close()

if __name__ == "__main__":
    main()
