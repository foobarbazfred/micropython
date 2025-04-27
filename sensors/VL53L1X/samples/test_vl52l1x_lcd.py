#
# test program for VL53L1X Driver with LCD
#
from machine import I2C
from machine import Pin
import time
from vl53l1x import VL53L1X
from st7032 import ST7032LCD

# i2c setting for Sensor
# default setting :  SCL:Pin(5), SDA:Pin(4)
i2c = I2C(0, scl=Pin(5), sda=Pin(4),  freq=10_000) 
tof = VL53L1X(i2c)

# i2c setting for LCD
# default setting :  SCL:Pin(19), SDA:Pin(18)
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10_000)
lcd = ST7032LCD(i2c)

lcd.cls()  # clear screen

distance_mode = 'long'
tof.set_distance_mode(distance_mode)
tof.start_measurement()

while True:
  if tof.get_data_ready():
     distance = tof.get_distance()
     print(f"dist: {distance} cm")
     cld.print(f"dist:{distance}\n mode:{distance_mode}")
     tof.clear_interrupt()
  else:
     time.sleep_ms(100)

tof.stop_measurement()
