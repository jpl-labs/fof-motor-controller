import pigpio

from .logging_handler import LoggingHandler
from .pin_mode import PinMode


class PiHeader(LoggingHandler):

    def __init__(self, mode=PinMode.BCM):
        super(PiHeader, self).__init__()

        if mode != PinMode.BCM:
            raise NotImplementedError('Board numbering not yet implemented')

        self.pi = pigpio.pi()
        self.used_pins = []

    def get_pin(self, pinNumber, pinType):
        self.logger.debug('Creating pin on gpio %s', pinNumber)
        newPin = pinType(self, int(pinNumber))
        self.used_pins.append(newPin)
        return newPin

    def __enter__(self):
        return self

    def __getitem__(self, pinNumber):
        return Pin(self, pinNumber)

    def __exit__(self, exc_type, exc_value, traceback):
        self.pi.close()
