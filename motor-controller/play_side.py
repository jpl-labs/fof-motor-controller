import RPi.GPIO as GPIO

class PlaySide(object):

    def __init__(self, motor, fan_device, pir_score_pin, button_pin):
        self.motor = motor
        self.fan_device = fan_device
        self.pir_score_pin = pir_score_pin
        self.motor.button_pin = button_pin

        print('GAME: setting up pir on pin:' + str(self.pir_score_pin))
        GPIO.setup(self.pir_score_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # The PIR sensor has its own debouncing resistor. Its minimum possible
        # duration is 2500ms.
        GPIO.add_event_detect(self.pir_score_pin, GPIO.FALLING,
                              callback=self.score_change_sensed_event, bouncetime=2500)

    def score_change_sensed_event(self, channel):
        print('GAME: score changed ' + str(channel))
        score_changed(self)

    def score_changed(playSide):
        send_websocket_message(DeviceScoreChangeEvent(playSide.fan_device))

