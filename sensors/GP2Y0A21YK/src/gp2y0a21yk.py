#
# GP2Y0A21YK
# v0.02 (2025/2/11)
#

import time
from machine import ADC, Pin

SENSOR_MEASUREMENT_TIMING = 40  # interval 40msec
SAMPLIG_SIZE = 21

LCD_AVAILABLE = True

adc = ADC(Pin(26))     # 

if LCD_AVAILABLE:
   from st7032 import ST7032LCD
   from machine import I2C
   i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10000) # OK??
   lcd =  ST7032LCD(i2c)

def median_filter(value_list):
    calc_buf  = value_list.copy()
    calc_buf.sort()
    center_value = calc_buf[int(len(calc_buf)/2)]
    return center_value


value_list = [0] * SAMPLIG_SIZE

def measure_distance():
    global value_list
    # sampling data for fill value_list
    for _ in range(SAMPLIG_SIZE):
        raw_vol = 3.3 * adc.read_u16() / 65535
        value_list.append(raw_vol)
        _ = value_list.pop(0)     # to avoid print out
        time.sleep_us(300)  # wait for avoid power line noise (interval 1ms)
        time.sleep_ms(SENSOR_MEASUREMENT_TIMING)  # wait until sensor output is updated

    filterd_value = median_filter(value_list)
    estim_dist = 28.26 / filterd_value
    return estim_dist, filterd_value


while True:
    dist, vol = measure_distance()
    report = f'dist: {dist:4.1f}cm\nvol: {vol:4.2f}v'
    print('----------------------------------')
    print(report)
    lcd.print(report,cls=True)

