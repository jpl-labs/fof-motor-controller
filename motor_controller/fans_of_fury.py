import asyncio

from .fan_device import FanDevice
from .motor import Motor
from .device_controller import DeviceController
from .play_side import PlaySide
from .input_pin import InputPin
from .hardware_pwm_pin import HardwarePWMPin
from .dead_mans_switch import DeadMansSwitch


class FansOfFury(object):

    def __init__(self, config, header):
        self.loop = asyncio.get_event_loop()
        self.header = header
        self.config = config

        GPIO_PIN_PIR_1 = config['gpio']['pin_pir_1']
        GPIO_PIN_PIR_2 = config['gpio']['pin_pir_2']

        self.switches = [DeadMansSwitch(header.get_pin(config['gpio']['switch_1'], InputPin)), DeadMansSwitch(header.get_pin(
            config['gpio']['switch_2'], InputPin))]

        self.motors = [Motor(header.get_pin(config['gpio']['pin_out_1'], HardwarePWMPin), config['motor'], self.switches[0]),
                       Motor(header.get_pin(config['gpio']['pin_out_2'], HardwarePWMPin), config['motor'], self.switches[1])]

        self.fans = [FanDevice(config['fan']['min_input_value'], self.motors[0].MAX_PERCENTAGE, '0', 'fan'),
                     FanDevice(config['fan']['max_input_value'], self.motors[1].MAX_PERCENTAGE, '1', 'fan')]

        self.device_controller_config = DeviceController('0', self.fans)

        self.PLAY_SIDES = [PlaySide(self.motors[0], self.fans[0], GPIO_PIN_PIR_1, self.switches[0]), PlaySide(
            self.motors[1], self.fans[1], GPIO_PIN_PIR_2, self.switches[1])]
