from .logging_handler import LoggingHandler
from .pin import Pin

class HardwarePWMPin(Pin, LoggingHandler):

    def __init__(self, header, pinNumber):
        super(HardwarePWMPin, self).__init__(header, pinNumber)
