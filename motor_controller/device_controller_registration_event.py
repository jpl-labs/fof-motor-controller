class DeviceControllerRegistrationEvent(object):

    def __init__(self, device_controller):
        self.device_controller = device_controller
        self.message_type = 'DEVICE_CONTROLLER_REGISTRATION'
