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
        newPin = pinType(self, pinNumber)

        self.used_pins.append(newPin)

    def __enter__(self):
        return self

    def __getitem__(self, pinNumber):
        return Pin(self, pinNumber)

    def __exit__(self, exc_type, exc_value, traceback):
        del self.pwm


class Pin(LoggingHandler):

    def __init__(self, header, pin_number):
        super(Pin, self).__init__()
        self.header = header
        self.pin_number = pin_number
