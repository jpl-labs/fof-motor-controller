import time
from datetime import datetime
from time import sleep

from .logging_handler import LoggingHandler


class Motor(LoggingHandler):

    def __init__(self, gpioPinOut, config, speed=None):
        super(Motor, self).__init__()
        self.MIN_PERCENTAGE = int(config['min_pct'])
        self.MAX_PERCENTAGE = int(config['max_pct'])
        self.NEUTRAL_DUTY_CYCLE = config['neutral_duty_cycle']
        self.SCALE_FACTOR = config['scale_factor']
        self.MAX_DUTY_PCT = config['max_duty_pct']
        self.DUTY_CYCLE_STEP = config['duty_cycle_step']
        self.current_pct = self.MIN_PERCENTAGE
        self.pwm = gpioPinOut

        self.last_event_date = datetime.now()

        self.logger.debug('Initializing motor on gpio:%s', self.pwm.pin_number)

        # The motors will not start spinning until they've exceeded 10% of the
        # possible duty cycle range. This means initialization must be 1 to
        # 100%, and the motors will start spinning at 11%.'
        self.logger.debug('Arming motors, part 1. Moving to 1%')

        self.pwm.frequency=config['pwm_frequency']
        self.pwm.range=100
        self.pwm.duty_cycle = 1

        time.sleep(2)

        self.logger.debug('Arming motors, part 2. Moving to 100%')
        self.pwm.duty_cycle = 100
        time.sleep(2)
        self.logger.debug('Arming done. Moving to 1%')
        self.pwm.duty_cycle = 1
        time.sleep(2)

        self.current_pct = 0

        if speed is None:
            self.desired_speed = self.MIN_PERCENTAGE
        else:
            self.desired_speed = speed

        self.logger.info(
            'Motor on gpio %s ready for action', self.pwm.pin_number)

    def __enter__(self):
        return self

    @property
    def actual_speed(self):
        return round((self.pwm.value - 50) / 0.22)

    @property
    def desired_speed(self):
        return self.current_pct

    @desired_speed.setter
    def desired_speed(self, percent):
        self.logger.debug(
            'Setting pwd on gpio: %s to %s', self.pwm.pin_number, percent)

        while self.current_pct > percent:
            self.current_pct -= 1
            self.pwm.value = self.desired_duty_cycle
            sleep(0.02)

        while self.current_pct < percent:
            self.current_pct += 1
            self.pwm.value = self.desired_duty_cycle
            sleep(0.02)

        self.logger.debug('Done setting pwd on gpio: %s to %s', self.pwm.pin_number, percent)

    def min_speed(self):
        self.desired_speed = self.MIN_PERCENTAGE

    def max_speed(self):
        self.desired_speed = self.MAX_PERCENTAGE

    @property
    def desired_duty_cycle(self):
        return (0.22 * self.current_pct) + 50

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug('Shutting down motor on gpio: %s', self.pwm.pin_number)
        del self.pwm
