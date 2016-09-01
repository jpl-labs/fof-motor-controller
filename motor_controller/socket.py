import json
from datetime import datetime

from autobahn.asyncio.websocket import WebSocketClientProtocol


from .fan_device import FanDevice
from .fan_speed_change_event import FanSpeedChangeEvent
from .device_controller_registration_event import DeviceControllerRegistrationEvent
from .logging_handler import LoggingHandler
from .__main__ import fans_of_fury


class Socket(LoggingHandler, WebSocketClientProtocol):

    def __init__(self):
        super(Socket, self).__init__()
        self.fof = fans_of_fury

    def onOpen(self):
        self.logger.info('Socket opened')

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
            if new_value > self.fof.PLAY_SIDES[fan_id].motor.MIN_PERCENTAGE:
                self.fof.PLAY_SIDES[
                    fan_id].motor.last_event_date = datetime.now()

    def onClose(self, wasClean, code, reason):
        if reason:
            self.logger.warn(reason)
        self.fof.stop()
