import time
from machine import Pin
from hc-sr04 import HC-SR04

LCD_AVAILABLE = True
trig = Pin(14, Pin.OUT)
echo = Pin(15, Pin.IN)
hc_sr04 = HC-SR04(trig,echo)

if LCD_AVAILABLE:
   from st7032 import ST7032LCD
   from machine import I2C
   i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10000) # OK??
   lcd =  ST7032LCD(i2c)

while True:
  distance, pulse_width = hc_sr04.measure()   # 
  #print(pulse_width)

  report = f"dist: {distance:0.2f}cm\npulse: {pulse_width}usec"
  print("-------------------")
  print(report)
  if LCD_AVAILABLE:
     lcd.print(report, cls=True)
  time.sleep(0.5)


