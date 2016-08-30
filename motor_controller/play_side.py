import logging

from gpiocrust import InputPin

class PlaySide(object):

    def __init__(self, motor, fan_device, pir_score_pin, button_pin):
        self.motor = motor
        self.fan_device = fan_device
        self.pir_score_pin = pir_score_pin
        self.motor.button_pin = button_pin
        InputPin(self.pir_score_pin, callback=self.score_change_sensed_event)


    def score_change_sensed_event(self, channel):
        logging.debug('GAME: score changed ' + str(channel))
        self.score_changed()

    def score_changed(playSide):
        send_websocket_message(DeviceScoreChangeEvent(playSide.fan_device))

