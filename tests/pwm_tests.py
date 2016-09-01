import time

import pigpio

pi = pigpio.pi()

pi.hardware_PWM(19, 500, 10000)

#pi.set_PWM_frequency(15, 500)
#pi.set_PWM_range(15, 100)
#pi.set_PWM_dutycycle(15, 1)

time.sleep(2)

pi.hardware_PWM(19, 500, 1000000)

#pi.set_PWM_dutycycle(15, 100)

time.sleep(2)

pi.hardware_PWM(19, 500, 10000)

#pi.set_PWM_dutycycle(15, 1)

time.sleep(2)

pi.hardware_PWM(19, 500,600000)

#pi.set_PWM_dutycycle(15, 50)

time.sleep(5)
