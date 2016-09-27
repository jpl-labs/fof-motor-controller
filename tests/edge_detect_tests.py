import pigpio
import time

pi = pigpio.pi()

def cbf1(gpio, level, tick):
	print('down')
def cbf2(gpio, level, tick):
	print('up')

pi.set_glitch_filter(25, 1000)
pi.set_glitch_filter(8, 1000)

pi.set_mode(25, pigpio.INPUT)
pi.set_pull_up_down(25, pigpio.PUD_DOWN)
cb1 = pi.callback(25, pigpio.RISING_EDGE, cbf1)
cb4 = pi.callback(25, pigpio.FALLING_EDGE, cbf2)



pi.set_mode(8, pigpio.INPUT)
pi.set_pull_up_down(8, pigpio.PUD_DOWN)
cb2 = pi.callback(8, pigpio.RISING_EDGE, cbf1)
cb3 = pi.callback(8, pigpio.FALLING_EDGE, cbf2)

while(True):
	time.sleep(10)
	print('.')


