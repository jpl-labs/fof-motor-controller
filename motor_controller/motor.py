import time
from datetime import datetime
import logging
from time import sleep

from gpiocrust import PWMOutputPin


class Motor(object):

    def __init__(self, gpioPinOut, motorConfig, speed=None):
        self.MIN_PERCENTAGE = int(motorConfig['min_pct'])
        self.MAX_PERCENTAGE = int(motorConfig['max_pct'])
        self.NEUTRAL_DUTY_CYCLE = motorConfig['neutral_duty_cycle']
        self.SCALE_FACTOR = motorConfig['scale_factor']
        self.MAX_DUTY_PCT = motorConfig['max_duty_pct']
        self.DUTY_CYCLE_STEP = motorConfig['duty_cycle_step']
        self.current_pct = self.MIN_PERCENTAGE
        self.gpio_out = gpioPinOut

        self.last_event_date = datetime.now()

        logging.debug(
            'MOTOR: Initializing motor on gpio:{motor.gpio_out}'.format(motor=self))
        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%.'
        logging.debug('MOTOR: Arming motors, part 1. Moving to 1%')

        self.pwm = PWMOutputPin(self.gpio_out, frequency=float(
            motorConfig['pwm_frequency']), value=0.01)

        time.sleep(2)
        logging.debug('MOTOR: Arming motors, part 2. Moving to 100%')
        self.pwm.value = 1
        time.sleep(2)
        logging.debug('MOTOR: Arming done. Moving to 1%')
        self.pwm.value = 0.01
        time.sleep(2)
        self.current_pct = 0

        if speed is None:
            self.desired_speed = self.MIN_PERCENTAGE
        else:
            self.desired_speed = speed

        logging.debug(
            'Motor on gpio {motor.gpio_out} ready for action'.format(motor=self))

    def __enter__(self):
        return self

    @property
    def actual_speed(self):
        return round((self.pwm.value - 0.5) / 0.0022)

    @property
    def desired_speed(self):
        return self.current_pct

    @desired_speed.setter
    def desired_speed(self, percent):
        logging.debug(
            'setting pwd on gpio: {motor.gpio_out} to {motor.desired_duty_cycle}'.format(motor=self))

        while self.current_pct > percent:
            self.current_pct -= 1
            self.pwm.value = self.desired_duty_cycle
            sleep(0.02)

        while self.current_pct < percent:
            self.current_pct += 1
            self.pwm.value = self.desired_duty_cycle
            sleep(0.02)

        logging.debug('done setting pwd on gpio: {motor.gpio_out} to {motor.desired_duty_cycle}'.format(
            motor=self))

    def min_speed(self):
        self.desired_speed = self.MIN_PERCENTAGE

    def max_speed(self):
        self.desired_speed = self.MAX_PERCENTAGE

    @property
    def desired_duty_cycle(self):
        return (0.0022 * self.current_pct) + 0.5

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug('shutting down motor on gpio:' + str(self.gpio_out))
        del self.pwm