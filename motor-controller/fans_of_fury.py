import logging
from datetime import datetime

import RPi.GPIO as GPIO

from .motor import Motor
from .fan_device import FanDevice
from .device_controller import DeviceController
from .play_side import PlaySide


class FansOfFury(object):

    def __init__(self, gameConfig):
        GPIO.setmode(GPIO.BCM)

        GPIO_PIN_OUT_1 = gameConfig['gpio']['pin-out-1']
        GPIO_PIN_OUT_2 = gameConfig['gpio']['pin-out-2']
        GPIO_PIN_PIR_1 = gameConfig['gpio']['pin-pir-1']
        GPIO_PIN_PIR_2 = gameConfig['gpio']['pin-pir-2']

        GPIO_SWITCH_1 = gameConfig['gpio']['switch-1']
        GPIO_SWITCH_2 = gameConfig['gpio']['switch-2']

        self.MOTORS = [Motor(GPIO_PIN_OUT_1, gameConfig['motor']),
                       Motor(GPIO_PIN_OUT_2, gameConfig['motor'])]

        self.fans = [FanDevice(gameConfig['fan']['min_input_value'], self.MOTORS[0].MAX_PERCENTAGE, '0', 'fan'),
                     FanDevice(gameConfig['fan']['max_input_value'], self.MOTORS[1].MAX_PERCENTAGE, '1', 'fan')]

        self.device_controller_config = DeviceController('0', self.fans)

        # setup switches, gpio 25 on side 1, gpio 8 on side 2
        GPIO.setup(GPIO_SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(GPIO_SWITCH_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.PLAY_SIDES = [PlaySide(self.MOTORS[0], self.fans[0], GPIO_PIN_PIR_1, GPIO_SWITCH_1), PlaySide(
            self.MOTORS[1], self.fans[1], GPIO_PIN_PIR_2, GPIO_SWITCH_2)]

    def __enter__(self):
        return self

    def emergency_stop(self):
        now = datetime.now()
        for x in range(0, len(self.MOTORS)):
            if self.PLAY_SIDES[x].motor.current_pct > self.PLAY_SIDES[x].motor.MIN_PERCENTAGE and (now - self.PLAY_SIDES[x].motor.last_event_date).seconds >= 10:
                logging.debug('No speed events received for Play Side ' +
                              str(x) + ' in > 10 seconds, dropping to min speed')
                self.PLAY_SIDES[x].motor.minSpeed()

    def __exit__(self, *args):
        logging.debug('shutting down fof')

        for motor in self.MOTORS:
            motor.min_speed()
            motor.__exit__(*args)
