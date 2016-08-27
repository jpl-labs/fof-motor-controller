import configparser

from motor_controller import Motor

cfg = configparser.ConfigParser()
cfg.read('motor_controller/config.ini')


def test_motor_init():
    motor = Motor(0, cfg['motor'])
    assert motor.desired_speed == int(cfg['motor']['min_pct'])
    assert motor.pwm.value == motor.desired_duty_cycle
    assert motor.actual_speed == int(cfg['motor']['min_pct'])

def test_motor_increase_speed():
    motor = Motor(0, cfg['motor'])

    motor.desired_speed = 50
    assert motor.pwm.value == motor.desired_duty_cycle
    assert motor.actual_speed == 50

def test_motor_decrease_speed():
    motor = Motor(0, cfg['motor'], speed=100)
    assert motor.actual_speed == 100

    motor.desired_speed = 80
    assert motor.pwm.value == motor.desired_duty_cycle
    assert motor.actual_speed == 80

