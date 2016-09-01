import configparser
import time

from motor_controller import Motor, PiHeader, PinMode, HardwarePWMPin

cfg = configparser.ConfigParser()
cfg.read('motor_controller/config.ini')


def test_motor_init():
    with PiHeader(mode=PinMode.BCM) as header:
        motor = Motor(header.get_pin(
            cfg['gpio']['pin_out_1'], HardwarePWMPin), cfg['motor'])
        assert motor.desired_speed == int(cfg['motor']['min_pct'])
        assert motor.pwm.value == motor.desired_duty_cycle
        assert motor.actual_speed == int(cfg['motor']['min_pct'])


def test_motor_increase_speed():
    with PiHeader(mode=PinMode.BCM) as header:
        motor = Motor(header.get_pin(
            cfg['gpio']['pin_out_1'], HardwarePWMPin), cfg['motor'])

        motor.desired_speed = 50
        time.sleep(5)
        assert motor.pwm.value == motor.desired_duty_cycle
        assert motor.actual_speed == 50


def test_motor_decrease_speed():
    with PiHeader(mode=PinMode.BCM) as header:
        motor = Motor(header.get_pin(
            cfg['gpio']['pin_out_1'], HardwarePWMPin), cfg['motor'])
        assert motor.actual_speed == 60
        time.sleep(5)
        motor.desired_speed = 50
        time.sleep(5)
        assert motor.pwm.value == motor.desired_duty_cycle
        assert motor.actual_speed == 50
