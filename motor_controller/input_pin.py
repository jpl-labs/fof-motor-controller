import pigpio

from .logging_handler import LoggingHandler
from .pin import Pin

class InputPin(Pin, LoggingHandler):

    def __init__(self, header, pinNumber):
        super(InputPin, self).__init__(header, pinNumber)

        self._header.pi.set_mode(self._pin_number, pigpio.INPUT)

    @property
    def value(self):
        return self._header.pi.read(self._pin_number)

    @property
    def pull(self):
        return self._header.pi.read(self._pin_number)

    @pull.setter
    def pull(self, val):
        if val:
            self._header.pi.set_pull_up_down(self._pin_number, pigpio.PUD_UP)
        else:
            self._header.pi.set_pull_up_down(self._pin_number, pigpio.PUD_DOWN)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._header.pi.set_pull_up_down(self._pin_number, pigpio.PUD_OFF)