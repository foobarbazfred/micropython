#
# sample program for touch sensor  AT42QT1011
#
# If the touch sensor AT42QT1011 is touched, 
# toggle the state flag control_state between True and False
#

from machine import Pin
import time

touch_sensor = Pin(15, Pin.IN)
led = Pin('LED', Pin.OUT)
led.off()
control_state = False
prev_sensor_value = 0


#
# interrupt handler  
#
# When the touch sensor is touched or released, 
# an interrupt occurs and this function is called
#
# in this function toggle state flag control_state
#
def intr_handler(arg0):
      global prev_sensor_value
      global control_state
      #
      # if touched then toggle flag
      #
      current_sensor_value = touch_sensor.value()
      if current_sensor_value != prev_sensor_value and current_sensor_value == 1:
         control_state = not control_state 
      prev_sensor_value = current_sensor_value

#
# set interrupt handler intr_handler
#
touch_sensor.irq(intr_handler, Pin.IRQ_FALLING | Pin.IRQ_RISING)

LOOP_DELAY = 20  # Add a 20 ms delay in the loop

#
# main loop
#
while True:
    if control_state == True:
        print('on')
        led.on()
    else:
        print('off ',end='')
        led.off()
    time.sleep_ms(LOOP_DELAY)


