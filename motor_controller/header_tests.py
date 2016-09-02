from motor_controller import PiHeader, PinMode, HardwarePWMPin, OutputPin, InputPin


def test_gpio_read():
    with PiHeader(mode=PinMode.BCM) as header:
        pin14 = header.get_pin(14, InputPin)
        assert pin14.value is False


def test_gpio_write():
    with PiHeader(mode=PinMode.BCM) as header:
        pin15 = header.get_pin(15, OutputPin)
        pin15.value = True
        assert pin15.value is True



def test_pwm():
    with PiHeader(mode=PinMode.BCM) as header:
        hw_pwm = header.get_pin(18, HardwarePWMPin)

        hw_pwm.frequency=500
        hw_pwm.range=100
        hw_pwm.duty_cycle = 1
        hw_pwm.duty_cycle = 60

        assert hw_pwm.actual_duty_cycle == 600000
