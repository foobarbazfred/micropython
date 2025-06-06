#
# test program for VL53L1X Driver
#

from machine import I2C
from machine import Pin
import time
from vl53l1x import VL53L1X

i2c = I2C(0, scl=Pin(5), sda=Pin(4),  freq=400_000, timeout=50_000) 
tof = VL53L1X(i2c)

tof.set_distance_mode('long')
tof.start_measurement()

while True:
  state = tof.wait_data_ready()
  if state:
     print(f"dist: {tof.get_distance()} cm")
     tof.clear_interrupt()
  else:
     print("Error: sensor error!!")
     print("Measurement failed")


tof.stop_measurement()
