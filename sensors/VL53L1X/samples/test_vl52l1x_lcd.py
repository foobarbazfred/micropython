#
# test program for VL53L1X Driver with LCD
#
from machine import I2C
from machine import Pin
import time
from vl53l1x import VL53L1X
from st7032 import ST7032LCD

# i2c setting for Sensor
i2c_0 = I2C(0, scl=Pin(5), sda=Pin(4),  freq=400_000, timeout=50_000) 
tof = VL53L1X(i2c_0)

# i2c setting for LCD
i2c_1 = I2C(1, scl=Pin(19), sda=Pin(18), freq=10_000)
lcd = ST7032LCD(i2c_1)

lcd.cls()  # clear screen

distance_mode = 'long'
tof.set_distance_mode(distance_mode)
tof.start_measurement()

while True:
  if tof.get_data_ready():
     distance = tof.get_distance()
     print(f"dist: {distance} cm")
     lcd.cls()
     lcd.print(f"dist:{distance}\nmode:{distance_mode}")
     tof.clear_interrupt()
     time.sleep(1)
  else:
     time.sleep_ms(100)

tof.stop_measurement()
