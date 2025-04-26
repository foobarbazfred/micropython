#
# driver for HC-SR04
#  v0.01 2025/2/11
#  v0.02 2025/4/26 refactor to class
#

from  machine import Pin
import time

TEMPERATURE = 24.0    # default 24.0 
SPEED_OF_SOUND = 331.45 + 0.61 * TEMPERATURE   # m / sec

MAX_TRY_COUNT = 65535

class HC-SR04:

    def __init__(self, trigger, echo):

        self._trigger = trigger
        self._echo = echo
        self._trigger.off()

    def measure(self):

        # generate High Pulse (width:10usec)
        self._trigger.on()
        time.sleep_us(10)
        self._trigger.off()
    

        # wait until ECHO H signal
        echo_on = None
        for _ in range(MAX_TRY_COUNT):
           if self._echo.value():
                echo_on = True
                break
        if not echo_on:
            print('internal error, can not find signal; ECHO H')
            return -1
        else:
            start = time.ticks_us()

        # wait until ECHO L signal
        echo_off = None
        for _ in range(MAX_TRY_COUNT):
            if not self._echo.value():
                echo_off = True
                break

        # measure time of Level H and calcurate distance
        if not echo_off:
            print('internal error, can not find signal; ECHO L')
            return -1
        else:
            pulse_width = time.ticks_diff(time.ticks_us(),start)
            distance = SPEED_OF_SOUND * pulse_width * 100  / ( 1000 * 1000) / 2 
            return (distance, pulse_width)


