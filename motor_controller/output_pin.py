import pigpio

from .logging_handler import LoggingHandler
from .pin import Pin

class OutputPin(Pin, LoggingHandler):

    def __init__(self, header, pinNumber):
        super(OutputPin, self).__init__(header, pinNumber)

        self._header.pi.set_mode(self._pin_number, pigpio.OUTPUT)

    @property
    def value(self):
        return self._header.pi.read(self._pin_number)

    @value.setter
    def value(self, val):
        self._header.pi.write(self._pin_number, val)
        self.logger.debug('Wrote %s to pin %s', val, self._pin_number)
