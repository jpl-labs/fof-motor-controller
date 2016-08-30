class DeviceScoreChangeEvent(object):

    def __init__(self, device):
        self.device = device
        self.messageType = 'DEVICE_SCORE_CHANGE'
