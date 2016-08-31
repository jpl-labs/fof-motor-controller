"""Main module to control the fan motors in the fans of fury game."""

import sys
import signal
import configparser
import logging
import json
from datetime import datetime

import asyncio
from gpiocrust import Header, PinMode
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

from .fan_device import FanDevice
from .fan_speed_change_event import FanSpeedChangeEvent
from .fans_of_fury import FansOfFury
from .device_controller_registration_event import DeviceControllerRegistrationEvent

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

logging.basicConfig(level=logging.DEBUG)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    def sigterm_handler(signum, frame):
        logging.info('GAME: received sigterm')
        loop.close()
        sys.exit()

    signal.signal(signal.SIGTERM, sigterm_handler)

    class FansOfFuryClientProtocol(WebSocketClientProtocol):

        def __init__(self):
            self.fof = None

        def onOpen(self):
            logging.debug('SOCKET: Socket opened')

            self.fof = FansOfFury(CONFIG)

            # Register this device controller and its devices
            registration_message = DeviceControllerRegistrationEvent(
                self.fof.device_controller_config)

            payload = json.dumps(registration_message, default=lambda o: o.__dict__,
                                 sort_keys=True, ensure_ascii=False).encode('utf8')
            logging.debug('SOCKET: Sending message through socket: %s', payload)
            self.sendMessage(payload, isBinary=False)

        def onMessage(self, payload, isBinary):
            logging.debug('Got message')
            if not isBinary:
                logging.debug('SOCKET: Received message:  %s', payload)
                dic = json.loads(payload.decode('utf8'))
                dic['device'] = FanDevice(**dic['device'])
                fan_speed_change_event = FanSpeedChangeEvent(**dic)
                logging.debug('SOCKET: New value: %s', fan_speed_change_event.newSpeed)
                fan_id = int(fan_speed_change_event.device.id)
                logging.debug('Fan ID is %s', fan_speed_change_event.device.id)
                new_value = float(fan_speed_change_event.newSpeed)

                self.fof.PLAY_SIDES[fan_id].motor.desired_speed = new_value
                if new_value > self.fof.PLAY_SIDES[fan_id].motor.MIN_PERCENTAGE:
                    self.fof.PLAY_SIDES[
                        fan_id].motor.last_event_date = datetime.now()

        def onClose(self, wasClean, code, reason):
            if reason:
                print(reason)
            loop.stop()

    with Header(mode=PinMode.BCM) as header:
        factory = WebSocketClientFactory(
            u'ws://192.168.31.99:8080/ws/fancontroller/websocket')
        factory.protocol = FansOfFuryClientProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, '192.168.31.99', 8080)
        loop.run_until_complete(coro)
        loop.run_forever()

    loop.close()

if __name__ == "__main__":
    main()
