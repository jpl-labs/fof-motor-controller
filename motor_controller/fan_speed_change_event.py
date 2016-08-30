class FanSpeedChangeEvent(object):

    def __init__(self, device, newSpeed):
        self.device = device
        self.newSpeed = newSpeed
