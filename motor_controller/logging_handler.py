import logging

class LoggingHandler(object):
	def __init__(self, *args, **kwargs):
		super(LoggingHandler, self).__init__()
		self.logger = logging.getLogger(self.__class__.__name__)
