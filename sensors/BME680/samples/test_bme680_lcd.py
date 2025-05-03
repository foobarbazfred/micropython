#
# test program for BME680 with LCD
#

import time
from machine import Pin
from machine import I2C
from bme680 import BME680_I2C

BME680_ADDR = 0x77
BME680_I2C_0 = 0
BME680_I2C_SDA = 4
BME680_I2C_SCL = 5
BME680_I2C_FREQ = 10_000  # freq 10KHz

from st7032 import ST7032LCD
LCD_I2C_1 = 1
LCD_I2C_SDA = 18
LCD_I2C_SCL = 19
LCD_I2C_FREQ = 10_000  # freq 10KHz

def main():

    bme_i2c = I2C(BME680_I2C_0, scl = Pin(BME680_I2C_SCL), sda = Pin(BME680_I2C_SDA), freq = BME680_I2C_FREQ) 
    if BME680_ADDR in bme_i2c.scan():
        print("BME680 connection is OK")
    else:
        print("Error; BME680 is not connected")
    
    bme = BME680_I2C(bme_i2c)

    lcd_i2c = I2C(LCD_I2C_1, scl = Pin(LCD_I2C_SCL), sda = Pin(LCD_I2C_SDA), freq = LCD_I2C_FREQ)
    lcd =  ST7032LCD(lcd_i2c)

    nth = 0
    while True:
        temperature = bme.temperature
        humidity = bme.humidity
        pressure = bme.pressure
        gas = bme.gas
      
        print('---------------------------------')
        print(f'temp: {temperature:0.2f} C')
        print(f'hum:  {humidity:0.2f} %')
        print(f'press: {pressure:0.2f} hPa')
        print(f'gas: {gas}')
     
        msg_temp = f'temp: {temperature:0.2f} C'
        msg_hum = f'hum:  {humidity:0.2f} %'
        msg_press = f'prs: {pressure:0.2f} hPa'
        msg_gas = f'gas: ({gas})'
        msg_list = (msg_temp, msg_hum, msg_press, msg_gas)

        selected_msg = msg_list[nth] + '\n' + msg_list[nth + 1]
        lcd.print(selected_msg, cls = True)
        nth += 2
        if nth == 4:
           nth = 0
     
        time.sleep(1)
         

main()

#
# end of file
#
