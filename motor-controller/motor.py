import time
from datetime import datetime
import logging

import RPi.GPIO as GPIO


class Motor(object):

    def __init__(self, gpioPinOut, motorConfig):
        self.MIN_PERCENTAGE = motorConfig['min_pct']
        self.MAX_PERCENTAGE = motorConfig['max_pct']
        self.NEUTRAL_DUTY_CYCLE = motorConfig['neutral_duty_cycle']
        self.SCALE_FACTOR = motorConfig['scale_factor']
        self.MAX_DUTY_PCT = motorConfig['max_duty_pct']
        self.DUTY_CYCLE_STEP = motorConfig['duty_cycle_step']
        self.current_pct = self.MIN_PERCENTAGE
        self.is_initializing = False
        self.gpio_out = gpioPinOut
        GPIO.setup(self.gpio_out, GPIO.OUT)

        self.pwm = GPIO.PWM(self.gpio_out, motorConfig['pwm_frequency'])
        self.last_event_date = datetime.now()

        logging.debug(
            'MOTOR: Initializing motor on gpio:{motor.gpio_out}'.format(motor=self))
        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%.'
        logging.debug('MOTOR: Arming motors, part 1. Moving to 1%')
        self.pwm.start(1)
        time.sleep(2)
        logging.debug('MOTOR: Arming motors, part 2. Moving to 100%')
        self.pwm.ChangeDutyCycle(100)
        time.sleep(2)
        logging.debug('MOTOR: Arming done. Moving to 1%')
        self.pwm.ChangeDutyCycle(1)
        time.sleep(2)
        logging.debug('MOTOR: Setting duty cycle to ' + str(40))
        self.pwm.ChangeDutyCycle(40)
        self.current_pct = self.MIN_PERCENTAGE
        self.is_initializing = False
        logging.debug(
            'Motor on gpio {motor.gpio_out} ready for action'.format(
                motor=self))

    def __enter__(self):
        return self

    def change_speed(self, percent):
        logging.debug(
            'setting pwd on gpio: {motor.gpio_out} to {motor.duty_cycle}'.format(motor=self))

        while self.current_pct > percent:
            self.current_pct = self.current_pct - 1
            self.pwm.ChangeDutyCycle(self.duty_cycle)

        while self.current_pct < percent:
            self.current_pct = self.current_pct + 1
            self.pwm.ChangeDutyCycle(self.duty_cycle)

        logging.debug('done setting pwd on gpio: {motor.gpio_out} to {motor.duty_cycle}'.format(
            motor=self))

    def min_speed(self):
        self.change_speed(self.MIN_PERCENTAGE)

    def max_speed(self):
        self.change_speed(self.MAX_PERCENTAGE)

    @property
    def duty_cycle(self):
        return 50 + (self.current_pct * 0.22)

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug('shutting down motor on gpio:' + str(self.gpio_out))
        self.pwm.stop()
        GPIO.cleanup(self.gpio_out)
