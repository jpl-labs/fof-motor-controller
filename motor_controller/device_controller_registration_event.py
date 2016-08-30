class DeviceControllerRegistrationEvent(object):

    def __init__(self, device_controller):
        self.deviceController = device_controller
        self.messageType = 'DEVICE_CONTROLLER_REGISTRATION'
