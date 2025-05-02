#
# sample program for touch sensor  AT42QT1011
#
# If the AT42QT1011 is touched, then turn on the LED on the board
#
#

#touch sensor board
#  AT42QT1011 ... alternate mode touch switch
#  AT42QT1012 ... momentary mode ouch switch
#

from machine import Pin
import time

touch_sensor = Pin(15, Pin.IN)
led = Pin('LED', Pin.OUT)
led.off()

LOOP_DELAY = 20  # Add a 20 ms delay in the loop
TOUCHED_DELAY = 500   # Add a 500 ms delay when the touch sensor is touched


while True:
    if touch_sensor.value() == 0:
        print('.', end='')
        led.off()
    else:
        print('\n touched the sensor AT42QT1011', end='')
        led.on()
        time.sleep_ms(TOUCHED_DELAY)
    time.sleep_ms(LOOP_DELAY)


