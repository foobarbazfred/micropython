#
#  Pulse rate monitor with  MAX30100
#  V0.01 (2024/10/05)
#    modified:  changed current setting  of IR/RED LED 
#    https://github.com/devxplained/MAX3010x-Sensor-Library/blob/main/src/MAX30100.cpp
#    moving average N=10 (window size:10)
#  V0.02 (2025/5/6) refactor; create MAX30100 Driver
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
       diff = ir - prev_ir
       prev_ir = ir
       n_of_samples += 1

       # calc monving average
       buffer10.pop(0)
       buffer10.append(diff)

       ir_buffer100.pop(0)
       ir_buffer100.append(ir)

       prev_filterd_data = filterd_data
       filterd_data = int(sum(buffer10)/len(buffer10))
       filterd_data = filterd_data * -1   #  reverse  wave form
       if filterd_data > 20 and prev_filterd_data <= 20 :
           min_val = min(ir_buffer100)
           if  min_val > 10000:   # to avoid  error miss 
                print('-------HHHHRRRR-----------', end='') 
                current_tick = time.ticks_us()
                delta = time.ticks_diff(current_tick,prev_tick)
                pbm = int(60 * 1000 * 1000 / delta)
                if pbm >= 50 and pbm <= 220:
                     print(pbm, int(delta/1000))
                else:
                     print('xxx', int(delta/1000))
                prev_tick = current_tick

       #
       # feed back by LED brink
       #
       if (n_of_samples % 2) == 0:   # down sampling 50 -> 25
           max_val = max(ir_buffer100)
           mean_val = int(sum(ir_buffer100)/len(ir_buffer100))
           min_val = min(ir_buffer100)
           if min_val > 10000:   #   normal setting of MAX1030 value of min
               brightness = int(0xffff * (max_val - ir) / (max_val - min_val))
           else:
               brightness = 0
           set_LED_brightness(led, brightness)
 
   return None




def main():

    #
    # device setup
    #

    # feed back led
    led = PWM(Pin(15), freq=500, duty_u16 = 0)
    
    #freq= 399_361
    
    i2c = I2C(0, scl=Pin(5),sda=Pin(4),freq=100_000)  # 100KHz
    #hex(i2c.scan()[0])
    
    if DEV_ADDR in i2c.scan():
        print('connection ok')
    else:
        print('check device connection')
    
    hr_sensor = MAX30100(i2c)
    hr_sensor.setup()
    
    #'0x57'
    #i2c.readfrom_mem(DEV_ADDR,0,1)
    #hr_sensor.read_temperature()

    #
    #  calcurate plus rate
    #
    calc_pulse_rate(hr_sensor, led)
    

main()


#
#
#
