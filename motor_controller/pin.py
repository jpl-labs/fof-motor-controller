from .logging_handler import LoggingHandler


class Pin(LoggingHandler):

    def __init__(self, header, pinNumber):
        super(Pin, self).__init__()

        self._header = header
        self._pin_number = pinNumber

    @property
    def pin_number(self):
        return self._pin_number