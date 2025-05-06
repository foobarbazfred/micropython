#
#  Pulse rate  monitor with  MAX30100
#  V0.01 (2024/10/05)
#    modified:  changed current setting  of IR/RED LED 
#    https://github.com/devxplained/MAX3010x-Sensor-Library/blob/main/src/MAX30100.cpp
#    moving average N=10 (window size:10)
#  V0.02 (2025/5/6) refactor; create MAX30100 Driver
#  V0.03 (2025/5/6) refactor; define constants
#
#

#
# create LED blink feed back (state of MAX30100 signal to visualize)
#
#


import time
import math
from machine import Pin
from machine import I2C
from machine import PWM

from max30100 import MAX30100

DEV_ADDR = 0x57


VALID_DIFFERENCE_THRESHOLD = 20

# threshold for Measurement is valid 
# any data must be larger than this value
MEASUREMENT_VALIDATION_THRESHOLD = 10000 



def set_LED_brightness(led, brightness):
    led.duty_u16(brightness)


def calc_pulse_rate(hr_sensor, led):

   hr_sensor.clear_ovfl_data()
   prev_ir = 0
   n_of_samples=0
   buffer10 = [0] * 10
   ir_buffer100 = [0] * 100
   filterd_data = 0
   prev_tick = time.ticks_us()

   while True:
       # wait until HR_RDY:H 
       while True:
          intr = hr_sensor.read_interrupt_status()
          if intr & 0b0010_0000:  # HR_RDY
              break
          else:
              pass

       data = hr_sensor.read_FIFO_data_4B()
       ir = (data[0] << 8) + data[1]

       # calc differential
       diff = ir - prev_ir
       prev_ir = ir
       n_of_samples += 1

       # add new data to queue (diffential)
       buffer10.pop(0)
       buffer10.append(diff)

       # add new data to queue (raw data)
       ir_buffer100.pop(0)
       ir_buffer100.append(ir)

       print(ir)

       # append moving average filter to diffential(N=10)
       prev_filterd_data = filterd_data
       filterd_data = int(sum(buffer10)/len(buffer10))
       filterd_data = filterd_data * -1   #  reverse  wave form

       # check cross the threshold
       if filterd_data > VALID_DIFFERENCE_THRESHOLD and prev_filterd_data <= VALID_DIFFERENCE_THRESHOLD:
           # Prevent false detections by ensuring the value is valid.
           min_val = min(ir_buffer100)
           if  min_val > MEASUREMENT_VALIDATION_THRESHOLD:   
                # if measured data is over THRESHOLD, then collect sampling
                print('-------HHHHRRRR-----------', end='') 
                current_tick = time.ticks_us()
                delta = time.ticks_diff(current_tick, prev_tick)
                pbm = int(60 * 1000 * 1000 / delta)
                if pbm >= 50 and pbm <= 220:   # display only if collect values.
                     print(pbm, int(delta/1000))
                else:                          # not display if abnormal values
                     print('xxx', int(delta/1000))
                prev_tick = current_tick

       #
       # feed back by LED brink
       #
       if (n_of_samples % 2) == 0:   # down sampling 50 -> 25
           max_val = max(ir_buffer100)
           mean_val = int(sum(ir_buffer100)/len(ir_buffer100))
           min_val = min(ir_buffer100)
           if min_val > MEASUREMENT_VALIDATION_THRESHOLD:   
               # blink LED only if in collect measuring
               brightness = int(0xffff * (max_val - ir) / (max_val - min_val))
           else:
               # if error, then turn off LED
               brightness = 0
           set_LED_brightness(led, brightness)
 
   return None




def main():

    #
    # device setup
    #

    # feed back led
    led = PWM(Pin(15), freq=500, duty_u16 = 0)

    # setup Heart Rate Sensor
    i2c0 = I2C(0, scl=Pin(5), sda=Pin(4), freq=100_000)  # 100KHz   
    if DEV_ADDR in i2c0.scan():
        print('connection ok')
    else:
        print('check device connection')
    
    hr_sensor = MAX30100(i2c0)
    hr_sensor.setup()
    
    #
    #  calcurate plus rate
    #
    calc_pulse_rate(hr_sensor, led)
    

main()


#
# end of file

#
