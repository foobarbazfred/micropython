from machine import Pin
from machine import I2C
from st7032 import ST7032LCD

i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10000)
lcd = ST7032LCD(i2c)

lcd.cls()  # clear screen
lcd.print('hello, world!\nare you fine??')
