class FanSpeedChangeEvent(object):

    def __init__(self, device, new_speed):
        self.device = device
        self.new_speed = new_speed
