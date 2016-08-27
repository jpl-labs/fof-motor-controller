import json
from datetime import datetime

import websocket

from .fan_device import FanDevice
from .fan_speed_change_event import FanSpeedChangeEvent
from .fans_of_fury import FansOfFury
from .device_controller_registration_event import DeviceControllerRegistrationEvent


class WebSocketHandler(object):

    def __init__(self, config):
        self.fof = None
        websocket.enableTrace(True)
        self.server_socket = websocket.WebSocketApp('ws://192.168.31.99:8080/ws/fancontroller/websocket',
                                                    on_message=self.on_message,
                                                    on_error=self.on_error,
                                                    on_close=self.on_close)
        self.config = config
        self.server_socket.on_open = self.on_open

    def __enter__(self):
        return self

    def run(self):
        self.server_socket.run_forever()

    def on_message(self, ws, message):
        print('SOCKET: Rec\'d message: ' + message)
        dic = json.loads(message)
        dic['device'] = FanDevice(**dic['device'])
        fan_speed_change_event = FanSpeedChangeEvent(**dic)
        print('SOCKET: New value: ' + str(fan_speed_change_event.new_speed))
        fan_id = int(fan_speed_change_event.device.id)
        print('Fan ID is ' + fan_speed_change_event.device.id)
        new_value = float(fan_speed_change_event.new_speed)

        self.fof.PLAY_SIDES[fan_id].motor.change_speed(new_value)
        if new_value > self.fof.PLAY_SIDES[fan_id].motor.MIN_PERCENTAGE:
            self.fof.PLAY_SIDES[fan_id].motor.last_event_date = datetime.now()

    def send_websocket_message(self, messageObject):
        if self.server_socket is None:
            print('SOCKET: Attempted to send message but web socket is not open!')

        if self.server_socket != None:
            msg = json.dumps(messageObject, default=lambda o: o.__dict__,
                             sort_keys=True, ensure_ascii=False).encode('utf8')
            print('SOCKET: Sending message through socket: ' + msg)
            self.server_socket.send(msg)

    def on_error(self, ws, error):
        print('SOCKET: Socket error: ' + str(error))

    def on_close(self, ws):
        print('SOCKET: ### socket closed ###')
        self.__exit__(None, None, None)

    def on_open(self, ws):
        print('SOCKET: Socket opened')

        self.fof = FansOfFury(self.config)
        self.server_socket = ws

        # Register this device controller and its devices
        registration_message = DeviceControllerRegistrationEvent(
            self.fof.device_controller_config)
        self.send_websocket_message(registration_message)

    def __exit__(self, *args):
        self.fof.__exit__(*args)
