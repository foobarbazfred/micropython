#
# HC-SR04 (2025/2/11)
#

from  machine import Pin
import time


TEMP = 24.0    # default 24.0 
SPEED_OF_SOUND = 331.45 + 0.61 * TEMP   # m / sec
LCD_AVAILABLE = True


trig = Pin(14, Pin.OUT)
echo = Pin(15, Pin.IN)
trig.off()

if LCD_AVAILABLE:
   from machine import I2C
   from st7032 import ST7032LCD
   i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10000) # OK??
   lcd =  ST7032LCD(i2c)

def measure(trig, echo):
   # generate High Pulse (width:10usec)
   trig.on()
   time.sleep_us(10)
   trig.off()

   # keisoku h width
   for _ in range(65535):
       if echo.value():
             break
   start = time.ticks_us()
   for _ in range(65535):
       if not echo.value():
             break
   pulse_width = time.ticks_diff(time.ticks_us(),start)
   return pulse_width

while True:
  pulse_width = measure(trig, echo)   # usec (1/ (1000 * 1000))
  #print(pulse_width)
  dist = SPEED_OF_SOUND * pulse_width * 100  / ( 1000 * 1000) / 2 
  report = f"dist: {dist:0.2f}cm\npulse: {pulse_width}usec"
  print("-------------------")
  print(report)
  if LCD_AVAILABLE:
     lcd.print(report, cls=True)
  time.sleep(0.5)

