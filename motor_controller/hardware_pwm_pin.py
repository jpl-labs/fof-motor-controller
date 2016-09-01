from .logging_handler import LoggingHandler
from .pin import Pin


class HardwarePWMPin(Pin, LoggingHandler):
    MAX_RANGE = 1000000

    def __init__(self, header, pinNumber):
        super(HardwarePWMPin, self).__init__(header, pinNumber)

        self._range_multiplier = 1
        self._frequency = 2000
        self._duty_cycle = 0

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, val):
        self._frequency = val
        self._header.pi.hardware_PWM(
            self._pin_number, self._frequency, self.actual_duty_cycle)

    @property
    def range(self):
        return HardwarePWMPin.MAX_RANGE / self._range_multiplier

    @range.setter
    def range(self, val):
        self._range_multiplier = HardwarePWMPin.MAX_RANGE / val

    @property
    def duty_cycle(self):
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, val):
        self._duty_cycle = val
        self._header.pi.hardware_PWM(
            self._pin_number, self._frequency, self.actual_duty_cycle)

    @property
    def actual_duty_cycle(self):
        return self.duty_cycle * self._range_multiplier

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.duty_cycle = 0
