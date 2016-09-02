import logging


class PlaySide(object):

    def __init__(self, motor, fan_device, pir_score_pin, button_pin):
        self.motor = motor
        self.fan_device = fan_device
        self.pir_score_pin = pir_score_pin
        self.motor.button_pin = button_pin
