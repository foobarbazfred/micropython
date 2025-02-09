import time
from machine import ADC, Pin

AVAILABLE_LCD = True

if AVAILABLE_LCD:
   import lcd
   lcd.lcd_cls(lcd.i2c)


adc = ADC(Pin(26))     # 

while True:
    adc_val = adc.read_u16()
    vol = 3.3 * adc_val / 65535
    estim_dist0 = 23.75 / (vol - 0.125) - 0.42   # specification
    estim_dist1 = 23.36 / (vol - 0.224) - 0.42    # local test
    estim_dist2 = 1 / (vol * 0.04388 - 0.007506) - 0.42    # local test2
    print('-------------------')
    print(estim_dist0, estim_dist1, estim_dist2)
    time.sleep(0.5)
