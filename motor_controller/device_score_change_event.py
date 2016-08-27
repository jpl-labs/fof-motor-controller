class DeviceScoreChangeEvent(object):

    def __init__(self, device):
        self.device = device
        self.message_type = 'DEVICE_SCORE_CHANGE'
