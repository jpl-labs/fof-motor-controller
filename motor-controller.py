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
callback_queue = Queue.Queue()


def from_dummy_thread(func_to_call_from_main_thread):
    callback_queue.put(func_to_call_from_main_thread)

    def resetFlag(self):
        self.motor.isInitializeing = False


# Support for emergency shutoff loop
from threading import Timer
from datetime import datetime


class FanDevice(object):

    def __init__(self, minInputValue, maxInputValue, id, type):
        self.minInputValue = minInputValue
        self.maxInputValue = maxInputValue
        self.id = id
        self.type = type

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class DeviceController(object):

    def __init__(self, id, devices):
        self.id = id
        self.devices = devices

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class DeviceControllerRegistrationEvent(object):

    def __init__(self, deviceController):
        self.deviceController = deviceController
        self.messageType = "DEVICE_CONTROLLER_REGISTRATION"

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class FanSpeedChangeEvent(object):

    def __init__(self, device, newSpeed):
        self.device = device
        self.newSpeed = newSpeed


class DeviceScoreChangeEvent(object):

    def __init__(self, device):
        self.device = device
        self.messageType = "DEVICE_SCORE_CHANGE"

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, ensure_ascii=False)


class Motor(object):

    def __init__(self, gpioPinOut):
        self.MIN_PERCENTAGE = 9
        self.MAX_PERCENTAGE = 80
        self.NEUTRAL_DUTY_CYCLE = 69
        self.SCALE_FACTOR = 0.14
        self.MAX_DUTY_PCT = 69
        self.DUTY_CYCLE_STEP = 1
        self.currentPct = self.MIN_PERCENTAGE
        self.gpioOut = gpioPinOut
        GPIO.setup(self.gpioOut, GPIO.OUT)

        self.pwm = GPIO.PWM(self.gpioOut, 500)
        self.lastEventDate = datetime.now()

    def changeSpeed(self, percent):
        print "GAME: setting pwd on gpio:" + str(self.gpioOut) + " to " + str(self.scalePercentageToDutyCycle(self.currentPct))
        if not GPIO.input(self.buttonPin):
            if (self.currentPct > percent):
                print "..............easing speed down..............."
                while self.currentPct > percent:
                    self.currentPct = self.currentPct - 1
                    self.pwm.ChangeDutyCycle(
                        self.scalePercentageToDutyCycle(self.currentPct))
            elif (self.currentPct < percent):
                print "..............easing speed up................"
                while self.currentPct < percent:
                    self.currentPct = self.currentPct + 1
                    self.pwm.ChangeDutyCycle(
                        self.scalePercentageToDutyCycle(self.currentPct))

            self.currentPct = percent
            self.pwm.ChangeDutyCycle(
                self.scalePercentageToDutyCycle(self.currentPct))
        else:
            if not self.isInitializing:
                self.isInitializing = True
                print "call self.rearmESC"
                threading.Thread(target=self.rearmESC, args=()).start()

    def minSpeed(self):
        self.changeSpeed(self.MIN_PERCENTAGE)

    def maxSpeed(self):
        self.changeSpeed(self.MAX_PERCENTAGE)

    def rearmESC(self):
        print "MOTOR: REARM Initializing motor on gpio:" + str(self.gpioOut)
        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%."
        print "MOTOR: Arming motors, part 1. Moving to 1%"
        self.pwm.start(1)
        time.sleep(2)
        print "MOTOR: Arming motors, part 2. Moving to 100%"
        self.pwm.ChangeDutyCycle(100)
        time.sleep(2)
        print "MOTOR: Arming done. Moving to 1%"
        self.pwm.ChangeDutyCycle(1)
        time.sleep(2)
        self.isInitializing = False
        print "MOTOR: Motor on gpio " + str(self.gpioOut) + " Ready for action"
        from_dummy_thread(lambda: resetFlag())

    def initialize(self):
        print "MOTOR: Initializing motor on gpio:" + str(self.gpioOut)
        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%."
        print "MOTOR: Arming motors, part 1. Moving to 1%"
        self.pwm.start(1)
        time.sleep(2)
        print "MOTOR: Arming motors, part 2. Moving to 100%"
        self.pwm.ChangeDutyCycle(100)
        time.sleep(2)
        print "MOTOR: Arming done. Moving to 1%"
        self.pwm.ChangeDutyCycle(1)
        time.sleep(5)
        print "MOTOR: Setting duty cycle to " + str(40)
        self.pwm.ChangeDutyCycle(40)
        self.currentPct = self.MIN_PERCENTAGE
        self.isInitializing = False
        print "MOTOR: Motor on gpio " + str(self.gpioOut) + " Ready for action"

    def scalePercentageToDutyCycle(self, percentage):
        return 50 + (percentage * 0.22)

    def shutdown(self):
        print "MOTOR: Shutting down motor on gpio:" + str(self.gpioOut)
        self.pwm.stop()
        GPIO.cleanup(self.gpioOut)


class PlaySide(object):

    def __init__(self, motor, fanDevice, pirScorePin, buttonPin):
        self.motor = motor
        self.fanDevice = fanDevice
        self.pirScorePin = pirScorePin
        self.motor.buttonPin = buttonPin

        print "GAME: setting up pir on pin:" + str(self.pirScorePin)
        GPIO.setup(self.pirScorePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # The PIR sensor has its own debouncing resistor. Its minimum possible
        # duration is 2500ms.
        GPIO.add_event_detect(self.pirScorePin, GPIO.FALLING,
                              callback=self.scoreChangeSensedEvent, bouncetime=2500)

    def scoreChangeSensedEvent(self, channel):
        print "GAME: score changed " + str(channel)
        scoreChanged(self)

    def initalize(self):
        self.motor.initialize()



def keyboardInputAvailable():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def shutdown():
    MOTORS[0].changeSpeed(MOTORS[0].MIN_PERCENTAGE)
    MOTORS[1].changeSpeed(MOTORS[1].MIN_PERCENTAGE)
    MOTORS[0].shutdown()
    MOTORS[1].shutdown()
    sys.exit()


def scoreChanged(playSide):
    sendWebsocketMessage(DeviceScoreChangeEvent(playSide.fanDevice))

GPIO.setmode(GPIO.BCM)

GPIO_PIN_OUT_1 = 15
GPIO_PIN_OUT_2 = 24
GPIO_PIN_PIR_1 = 14
GPIO_PIN_PIR_2 = 23

GPIO_SWITCH_1 = 25
GPIO_SWITCH_2 = 8

MOTORS = [Motor(GPIO_PIN_OUT_1), Motor(GPIO_PIN_OUT_2)]

fans = [FanDevice(2, MOTORS[0].MAX_PERCENTAGE, "0", "fan"),
        FanDevice(9, MOTORS[1].MAX_PERCENTAGE, "1", "fan")]

deviceControllerConfig = DeviceController("0", fans)

# setup switches, gpio 25 on side 1, gpio 8 on side 2
GPIO.setup(GPIO_SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_SWITCH_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PLAY_SIDES = [PlaySide(MOTORS[0], fans[0], GPIO_PIN_PIR_1, GPIO_SWITCH_1), PlaySide(
    MOTORS[1], fans[1], GPIO_PIN_PIR_2, GPIO_SWITCH_2)]

try:
    print "INIT: starting gpio version:" + GPIO.VERSION
    server_socket = None
    PLAY_SIDES[0].motor.initialize()
    PLAY_SIDES[1].motor.initialize()

    def emergencyStop():
        now = datetime.now()
        for x in range(0, len(MOTORS)):
            if PLAY_SIDES[x].motor.currentPct > PLAY_SIDES[x].motor.MIN_PERCENTAGE and (now - PLAY_SIDES[x].motor.lastEventDate).seconds >= 10:
                print "No speed events received for Play Side " + str(x) + " in > 10 seconds, dropping to min speed"
                PLAY_SIDES[x].motor.minSpeed()

    def parseJsonToObject(json):
        if 'messageType' in json:
            if json['messageType'] == 'FAN_SPEED_CHANGE':
                print "Fan speed change rec'd"
                device = parseJsonToObject(json.loads(json['device']))
                return FanSpeedChangeEvent(device, json['newSpeed'])
        elif 'fan' in json:
            if json['type'] == 'fan':
                return FanDevice(json['minInputValue'], json['maxInputValue'], json['id'], json['type'])
        return json

    def on_message(ws, message):
        print "SOCKET: Rec'd message: " + message
        dic = json.loads(message)
        dic['device'] = FanDevice(**dic['device'])
        fanSpeedChangeEvent = FanSpeedChangeEvent(**dic)
        print "SOCKET: New value: " + str(fanSpeedChangeEvent.newSpeed)
        fanId = int(fanSpeedChangeEvent.device.id)
        print "Fan ID is " + fanSpeedChangeEvent.device.id
        newValue = float(fanSpeedChangeEvent.newSpeed)
        PLAY_SIDES[fanId].motor.changeSpeed(newValue)
        if newValue > PLAY_SIDES[fanId].motor.MIN_PERCENTAGE:
            PLAY_SIDES[fanId].motor.lastEventDate = datetime.now()

    def on_error(ws, error):
        print "SOCKET: Socket error: " + str(error)

    def on_close(ws):
        print "SOCKET: ### socket closed ###"
        PLAY_SIDES[0].motor.minSpeed()
        PLAY_SIDES[1].motor.minSpeed()

    def on_open(ws):
        print "SOCKET: Socket opened"
        global server_socket
        server_socket = ws
        # Register this device controller and its devices
        registrationMessage = DeviceControllerRegistrationEvent(
            deviceControllerConfig)
        sendWebsocketMessage(registrationMessage)

    def sendWebsocketMessage(messageObject):
        if server_socket == None:
            print "SOCKET: Attempted to send message but web socket is not open!"

        if server_socket != None:
            msg = messageObject.toJson().encode('utf8')
            print "SOCKET: Sending message through socket: " + msg
            server_socket.send(msg)

    if __name__ == "__main__":
        # Loop for REAL forever
        print "SOCKET: Connecting to websocket server..."
        while 1:
            try:
                websocket.enableTrace(True)
                # Socket.io (underlying framework for websocket-client) requires '/websocket/' appended to the target URL so it can identify it as a websocket URL. Apparently ws:// protocol wasn't enough?
                # sp - my LAN IP is 192.168.21.41
                # sp - my wifi IP is 192.168.21.26
                # sp - server laptop is 192.168.21.36
                ws = websocket.WebSocketApp("ws://192.168.31.99:8080/ws/fancontroller/websocket",
                                            on_message=on_message,
                                            on_error=on_error,
                                            on_close=on_close)
                ws.on_open = on_open
                # 'run_forever' is a lie, like the cake. It actually exits when all sockets have closed.
                ws.run_forever()
            except:
                e = sys.exc_info()[1]
                print e
                print "SOCKET: Reconnecting..."
                time.sleep(20)

except KeyboardInterrupt:
    print "GAME: keyboard interrupt shutting down"
    PLAY_SIDES[0].motor.shutdown()
    PLAY_SIDES[1].motor.shutdown()
finally:
    shutdown()

print "GAME: final shutdown and cleanup"
shutdown()
