from .logging_handler import LoggingHandler
from .edges import Edges


class DeadMansSwitch(LoggingHandler):

    def __init__(self, pin):
        super(DeadMansSwitch, self).__init__()
        self.pin = pin
        self.pin.pull = True
        self.on_engage = self._noop
        self.on_release = self._noop
        self.pin.add_callback(Edges.FALLING, self._on_engage)
        self.pin.add_callback(Edges.RISING, self._on_release)

    def _noop(self):
        pass

    def _on_engage(self, *args, **kwargs):
        self.logger.info('Switch on gpio:%s engaged', self.pin._pin_number)
        self.on_engage()

    def _on_release(self, *args, **kwargs):
        self.logger.info('Switch on gpio:%s release', self.pin._pin_number)
        self.on_release()

    @property
    def active(self):
        return self.pin.value
