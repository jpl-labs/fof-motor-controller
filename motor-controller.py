import RPi.GPIO as GPIO
import time
import sys
# Support for keyboard input
import select
import termios
import tty
# For serialization/deserialization of objects
import json

# Websocket support
import websocket
import thread

# threading support
import Queue
import threading

# Project configuration
import configparser
import config as cfg

cfg = configparser.ConfigParser()
cfg.read('config.ini')

callback_queue = Queue.Queue()


def from_dummy_thread(func_to_call_from_main_thread):
    callback_queue.put(func_to_call_from_main_thread)

    def reset_flag(self):
        self.motor.isInitializeing = False


# Support for emergency shutoff loop
from threading import Timer
from datetime import datetime


class FanDevice(object):

    def __init__(self, min_input_value, max_input_value, id, type):
        self.min_input_value = min_input_value
        self.max_input_value = max_input_value
        self.id = id
        self.type = type

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class DeviceController(object):

    def __init__(self, id, devices):
        self.id = id
        self.devices = devices

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class DeviceControllerRegistrationEvent(object):

    def __init__(self, device_controller):
        self.device_controller = device_controller
        self.message_type = 'DEVICE_CONTROLLER_REGISTRATION'

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class FanSpeedChangeEvent(object):

    def __init__(self, device, new_speed):
        self.device = device
        self.new_speed = new_speed


class DeviceScoreChangeEvent(object):

    def __init__(self, device):
        self.device = device
        self.message_type = 'DEVICE_SCORE_CHANGE'

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class Motor(object):

    def __init__(self, gpioPinOut):
        self.MIN_PERCENTAGE = cfg['motor']['min_pct']
        self.MAX_PERCENTAGE = cfg['motor']['max_pct']
        self.NEUTRAL_DUTY_CYCLE = cfg['motor']['neutral_duty_cycle']
        self.SCALE_FACTOR = cfg['motor']['scale_factor']
        self.MAX_DUTY_PCT = cfg['motor']['max_duty_pct']
        self.DUTY_CYCLE_STEP = cfg['motor']['duty_cycle_step']
        self.current_pct = self.MIN_PERCENTAGE
        self.gpio_out = gpioPinOut
        GPIO.setup(self.gpio_out, GPIO.OUT)

        self.pwm = GPIO.PWM(self.gpio_out, cfg['motor']['pwm_frequency'])
        self.last_event_date = datetime.now()

    def change_speed(self, percent):
        print('GAME: setting pwd on gpio:'
              + str(self.gpio_out)
              + ' to '
              + str(self.scale_percentage_to_duty_cycle(self.current_pct)))
        if not GPIO.input(self.button_pin):
            if self.current_pct > percent:
                print('..............easing speed down...............')
                while self.current_pct > percent:
                    self.current_pct = self.current_pct - 1
                    self.pwm.ChangeDutyCycle(
                        self.scale_percentage_to_duty_cycle(self.current_pct))
            elif self.current_pct < percent:
                print('..............easing speed up................')
                while self.current_pct < percent:
                    self.current_pct = self.current_pct + 1
                    self.pwm.ChangeDutyCycle(
                        self.scale_percentage_to_duty_cycle(self.current_pct))

            self.current_pct = percent
            self.pwm.ChangeDutyCycle(
                self.scale_percentage_to_duty_cycle(self.current_pct))
        else:
            #		self.initialize()
            if not self.is_initializing:
                self.is_initializing = True
                print('call self.rearm_esc')
                threading.Thread(target=self.rearm_esc, args=()).start()

    def min_speed(self):
        self.change_speed(self.MIN_PERCENTAGE)

    def max_speed(self):
        self.change_speed(self.MAX_PERCENTAGE)

    def rearm_esc(self):
        print('MOTOR: REARM Initializing motor on gpio:' + str(self.gpio_out))
        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%.'
        print('MOTOR: Arming motors, part 1. Moving to 1%')
        self.pwm.start(1)
        time.sleep(2)
        print('MOTOR: Arming motors, part 2. Moving to 100%')
        self.pwm.ChangeDutyCycle(100)
        time.sleep(2)
        print('MOTOR: Arming done. Moving to 1%')
        self.pwm.ChangeDutyCycle(1)
        time.sleep(2)
#      print 'MOTOR: Setting duty cycle to ' + str(40)
#      self.pwm.ChangeDutyCycle(40)
#      self.current_pct = self.MIN_PERCENTAGE
        self.is_initializing = False
        print('MOTOR: Motor on gpio ' + str(self.gpio_out) + ' Ready for action')
        from_dummy_thread(lambda: reset_flag())

    def initialize(self):
        print('MOTOR: Initializing motor on gpio:' + str(self.gpio_out))
        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%.'
        print('MOTOR: Arming motors, part 1. Moving to 1%')
        self.pwm.start(1)
        time.sleep(2)
        print('MOTOR: Arming motors, part 2. Moving to 100%')
        self.pwm.ChangeDutyCycle(100)
        time.sleep(2)
        print('MOTOR: Arming done. Moving to 1%')
        self.pwm.ChangeDutyCycle(1)
        time.sleep(5)
        print('MOTOR: Setting duty cycle to ' + str(40))
        self.pwm.ChangeDutyCycle(40)
        self.current_pct = self.MIN_PERCENTAGE
        self.is_initializing = False
        print('MOTOR: Motor on gpio ' + str(self.gpio_out) + ' Ready for action')

    def scale_percentage_to_duty_cycle(self, percentage):
        return 50 + (percentage * 0.22)

    def shutdown(self):
        print('MOTOR: Shutting down motor on gpio:' + str(self.gpio_out))
        self.pwm.stop()
        GPIO.cleanup(self.gpio_out)


class PlaySide(object):

    def __init__(self, motor, fan_device, pir_score_pin, button_pin):
        self.motor = motor
        self.fan_device = fan_device
        self.pir_score_pin = pir_score_pin
        self.motor.button_pin = button_pin

        print('GAME: setting up pir on pin:' + str(self.pir_score_pin))
        GPIO.setup(self.pir_score_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # The PIR sensor has its own debouncing resistor. Its minimum possible
        # duration is 2500ms.
        GPIO.add_event_detect(self.pir_score_pin, GPIO.FALLING,
                              callback=self.score_change_sensed_event, bouncetime=2500)

    def score_change_sensed_event(self, channel):
        print('GAME: score changed ' + str(channel))
        score_changed(self)

    def initalize(self):
        self.motor.initialize()


def keyboard_input_available():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def shutdown():
    MOTORS[0].change_speed(MOTORS[0].MIN_PERCENTAGE)
    MOTORS[1].change_speed(MOTORS[1].MIN_PERCENTAGE)
    MOTORS[0].shutdown()
    MOTORS[1].shutdown()
    sys.exit()


def score_changed(playSide):
    send_websocket_message(DeviceScoreChangeEvent(playSide.fan_device))

GPIO.setmode(GPIO.BCM)

GPIO_PIN_OUT_1 = cfg['gpio']['pin-out-1']
GPIO_PIN_OUT_2 = cfg['gpio']['pin-out-2']
GPIO_PIN_PIR_1 = cfg['gpio']['pin-pir-1']
GPIO_PIN_PIR_2 = cfg['gpio']['pin-pir-2']

GPIO_SWITCH_1 = cfg['gpio']['switch-1']
GPIO_SWITCH_2 = cfg['gpio']['switch-2']

MOTORS = [Motor(GPIO_PIN_OUT_1), Motor(GPIO_PIN_OUT_2)]

fans = [FanDevice(cfg['fan']['min_input_value'], MOTORS[0].MAX_PERCENTAGE, '0', 'fan'),
        FanDevice(cfg['fan']['max_input_value'], MOTORS[1].MAX_PERCENTAGE, '1', 'fan')]

device_controller_config = DeviceController('0', fans)

# setup switches, gpio 25 on side 1, gpio 8 on side 2
GPIO.setup(GPIO_SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_SWITCH_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PLAY_SIDES = [PlaySide(MOTORS[0], fans[0], GPIO_PIN_PIR_1, GPIO_SWITCH_1), PlaySide(
    MOTORS[1], fans[1], GPIO_PIN_PIR_2, GPIO_SWITCH_2)]


try:
    print('INIT: starting gpio version:' + GPIO.VERSION)
    server_socket = None
    PLAY_SIDES[0].motor.initialize()
    PLAY_SIDES[1].motor.initialize()

    def emergency_stop():
        now = datetime.now()
        for x in range(0, len(MOTORS)):
            if PLAY_SIDES[x].motor.current_pct > PLAY_SIDES[x].motor.MIN_PERCENTAGE and (now - PLAY_SIDES[x].motor.last_event_date).seconds >= 10:
                print('No speed events received for Play Side ' + str(x) + ' in > 10 seconds, dropping to min speed')
                PLAY_SIDES[x].motor.minSpeed()
        # Reset the timer so this method will run again in 11 seconds
#    Timer(11.0, emergency_stop).start()

#  Timer(11.0, emergency_stop).start()

    def parse_json_to_object(json):
        if 'message_type' in json:
            if json['message_type'] == 'FAN_SPEED_CHANGE':
                print('Fan speed change rec\'d')
                device = parse_json_to_object(json.loads(json['device']))
                return FanSpeedChangeEvent(device, json['new_speed'])
        elif 'fan' in json:
            if json['type'] == 'fan':
                return FanDevice(json['min_input_value'], json['max_input_value'], json['id'], json['type'])
        return json

    def on_message(ws, message):
        print('SOCKET: Rec\'d message: ' + message)
        #fan_speed_change_event = json.loads(message, object_hook=parse_json_to_object)
        dic = json.loads(message)
        dic['device'] = FanDevice(**dic['device'])
        fan_speed_change_event = FanSpeedChangeEvent(**dic)
        print('SOCKET: New value: ' + str(fan_speed_change_event.new_speed))
        fan_id = int(fan_speed_change_event.device.id)
        print('Fan ID is ' + fan_speed_change_event.device.id)
        new_value = float(fan_speed_change_event.new_speed)
        PLAY_SIDES[fan_id].motor.change_speed(new_value)
        if new_value > PLAY_SIDES[fan_id].motor.MIN_PERCENTAGE:
            PLAY_SIDES[fan_id].motor.last_event_date = datetime.now()

    def on_error(ws, error):
        print('SOCKET: Socket error: ' + str(error))

    def on_close(ws):
        print('SOCKET: ### socket closed ###')
        PLAY_SIDES[0].motor.minSpeed()
        PLAY_SIDES[1].motor.minSpeed()

    def on_open(ws):
        print('SOCKET: Socket opened')
        global server_socket
        server_socket = ws
        # Register this device controller and its devices
        registration_message = DeviceControllerRegistrationEvent(
            device_controller_config)
        send_websocket_message(registration_message)

    def send_websocket_message(messageObject):
        if server_socket == None:
            print('SOCKET: Attempted to send message but web socket is not open!')

        if server_socket != None:
            msg = messageObject.to_json().encode('utf8')
            print('SOCKET: Sending message through socket: ' + msg)
            server_socket.send(msg)

    if __name__ == '__main__':
        # Loop for REAL forever
        print('SOCKET: Connecting to websocket server...')
        while 1:
            try:
                websocket.enableTrace(True)
                # Socket.io (underlying framework for websocket-client) requires '/websocket/' appended to the target URL so it can identify it as a websocket URL. Apparently ws:// protocol wasn't enough?
                # sp - my LAN IP is 192.168.21.41
                # sp - my wifi IP is 192.168.21.26
                # sp - server laptop is 192.168.21.36
                ws = websocket.WebSocketApp('ws://192.168.31.99:8080/ws/fancontroller/websocket',
                                            on_message=on_message,
                                            on_error=on_error,
                                            on_close=on_close)
                ws.on_open = on_open
                # 'run_forever' is a lie, like the cake. It actually exits when all sockets have closed.
                ws.run_forever()
            except:
                e = sys.exc_info()[1]
                print(e)
                print('SOCKET: Reconnecting...')
                time.sleep(20)

except KeyboardInterrupt:
    print('GAME: keyboard interrupt shutting down')
    PLAY_SIDES[0].motor.shutdown()
    PLAY_SIDES[1].motor.shutdown()
finally:
    shutdown()

print('GAME: final shutdown and cleanup')
shutdown()