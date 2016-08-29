import logging
from datetime import datetime

from gpiocrust import InputPin

from .motor import Motor
from .fan_device import FanDevice
from .device_controller import DeviceController
from .play_side import PlaySide


class FansOfFury(object):

    def __init__(self, gameConfig):
        print(gameConfig)
        print(gameConfig.sections())
        gpioconfig = gameConfig['gpio']
        GPIO_PIN_OUT_1 = gpioconfig['pin_out_1']
        GPIO_PIN_OUT_2 = gpioconfig['pin_out_2']
        GPIO_PIN_PIR_1 = gameConfig['gpio']['pin_pir_1']
        GPIO_PIN_PIR_2 = gameConfig['gpio']['pin_pir_2']

        GPIO_SWITCH_1 = gameConfig['gpio']['switch_1']
        GPIO_SWITCH_2 = gameConfig['gpio']['switch_2']

        self.MOTORS = [Motor(GPIO_PIN_OUT_1, gameConfig['motor']),
                       Motor(GPIO_PIN_OUT_2, gameConfig['motor'])]

        self.fans = [FanDevice(gameConfig['fan']['min_input_value'], self.MOTORS[0].MAX_PERCENTAGE, '0', 'fan'),
                     FanDevice(gameConfig['fan']['max_input_value'], self.MOTORS[1].MAX_PERCENTAGE, '1', 'fan')]

        self.device_controller_config = DeviceController('0', self.fans)

        self.switches = [InputPin(GPIO_SWITCH_1), InputPin(GPIO_SWITCH_2)]

        self.PLAY_SIDES = [PlaySide(self.MOTORS[0], self.fans[0], GPIO_PIN_PIR_1, self.switches[0]), PlaySide(
            self.MOTORS[1], self.fans[1], GPIO_PIN_PIR_2, self.switches[1])]

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

