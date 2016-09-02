import pigpio

from .logging_handler import LoggingHandler
from .pin import Pin
from .edges import Edges

EDGE_TO_PIGPIO = {
    Edges.RISING: pigpio.RISING_EDGE,
    Edges.FALLING: pigpio.FALLING_EDGE,
    Edges.EITHER: pigpio.EITHER_EDGE,
    Edges.NONE: None
}


class InputPin(Pin, LoggingHandler):

    def __init__(self, header, pinNumber):
        super(InputPin, self).__init__(header, pinNumber)

        self._header.pi.set_mode(self._pin_number, pigpio.INPUT)
        self._header.pi.set_glitch_filter(self._pin_number, 1000)
        self._callbacks = []

    @property
    def value(self):
        return self._header.pi.read(self._pin_number)

    @property
    def pull(self):
        return self._header.pi.read(self._pin_number)

    @pull.setter
    def pull(self, val):
        val = pigpio.PUD_UP if val else pigpio.PUD_DOWN
        self._header.pi.set_pull_up_down(self._pin_number, val)

    def add_callback(self, trigger, function):
        trigger = EDGE_TO_PIGPIO[trigger]
        callback = self._header.pi.callback(
            self._pin_number, trigger, function)
        self._callbacks.append(callback)
        return callback

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._header.pi.set_pull_up_down(self._pin_number, pigpio.PUD_OFF)
        for callback in self._callbacks:
            callback.cancel()
