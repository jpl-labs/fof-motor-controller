import time
from threading import Lock

from .logging_handler import LoggingHandler


class Motor(LoggingHandler):

    def __init__(self, gpioPinOut, config, dead_mans_switch=None, speed=None):
        super(Motor, self).__init__()
        self.MIN_PERCENTAGE = int(config['min_pct'])
        self.MAX_PERCENTAGE = int(config['max_pct'])
        self.NEUTRAL_DUTY_CYCLE = config['neutral_duty_cycle']
        self.SCALE_FACTOR = config['scale_factor']
        self.MAX_DUTY_PCT = config['max_duty_pct']
        self.DUTY_CYCLE_STEP = config['duty_cycle_step']
        self.INIT_WAIT = float(config['init_wait'])
        self.PWM_FREQUENCY = int(config['pwm_frequency'])
        self.pwm = gpioPinOut
        self.pwm_lock = Lock()
        self._enabled = True
        self._arm_motor()

        self.desired_speed = self._desired_speed = self.MIN_PERCENTAGE if speed is None else speed

        self.logger.info(
            'Motor on gpio %s ready for action', self.pwm.pin_number)

        self.dead_mans_switch = dead_mans_switch
        if dead_mans_switch is not None:
            dead_mans_switch.on_release = self.disable
            dead_mans_switch.on_engage = self.reenable
            self._enabled = False

    def _arm_motor(self):
        with (yield from self.pwm_lock):
            self.logger.debug('Initializing motor on gpio:%s',
                              self.pwm.pin_number)

            # The motors will not start spinning until they've exceeded 10% of the
            # possible duty cycle range. This means initialization must be 1 to
            # 100%, and the motors will start spinning at 11%.'
            self.logger.debug('Arming motors, part 1. Moving to 1%')

            self.pwm.frequency = self.PWM_FREQUENCY
            self.pwm.range = 100
            self.pwm.duty_cycle = 1

            time.sleep(self.INIT_WAIT)

            self.logger.debug('Arming motors, part 2. Moving to 100%')
            self.pwm.duty_cycle = 100

            time.sleep(self.INIT_WAIT)

            self.logger.debug('Arming done. Moving to 1%')
            self.pwm.duty_cycle = 1

            time.sleep(self.INIT_WAIT)

    def disable(self):
        self._enabled = False

        with (yield from self.pwm_lock):
            self.pwm.duty_cycle = 50

    def reenable(self):
        self._enabled = True

        with (yield from self.pwm_lock):
            self.pwm.duty_cycle = (0.22 * self._desired_speed) + 50

    @property
    def actual_speed(self):
        return round((self.pwm.value - 50) / 0.22)

    @property
    def desired_speed(self):
        return self._desired_speed

    @desired_speed.setter
    def desired_speed(self, percent):
        with (yield from self.pwm_lock):
            self._desired_speed = percent

            self.logger.debug(
                'Setting pwm on gpio: %s to %s', self.pwm.pin_number, self._desired_speed)

            while self.actual_speed != self._desired_speed and self._enabled:
                self.pwm.duty_cycle = self.next_duty_cycle
                time.sleep(0.02)

            self.logger.debug('Done setting pwm on gpio: %s to %s',
                              self.pwm.pin_number, self._desired_speed)

    def min_speed(self):
        self.desired_speed = self.MIN_PERCENTAGE

    def max_speed(self):
        self.desired_speed = self.MAX_PERCENTAGE

    @property
    def next_speed(self):
        diff = self._desired_speed - self.actual_speed

        if diff == 0:
            return self._desired_speed

        change = diff / abs(diff)

        return self.actual_speed + change

    @property
    def next_duty_cycle(self):
        return (0.22 * self.next_speed) + 50
