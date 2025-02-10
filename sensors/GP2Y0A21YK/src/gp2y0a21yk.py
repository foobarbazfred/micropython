#
# GP2Y0A21YK
#

import time
from machine import ADC, Pin

SENSOR_MEASUREMENT_TIMING = 40  # interval 40msec
AVAILABLE_LCD = True

if AVAILABLE_LCD:
   import lcd
   lcd.lcd_cls(lcd.i2c)

def median_filter(value_list):
    calc_buf  = value_list.copy()
    calc_buf.sort()
    center_value = calc_buf[int(len(calc_buf)/2)]
    return center_value

value_list = [0] * 21

adc = ADC(Pin(26))     # 

def measure_loop():
  while True:
    # sampling data for fill value_list
    for _ in range(len(value_list)):
        gp0.high()
        adc_val = adc.read_u16()
        gp0.low()
        raw_vol = 3.3 * adc_val / 65535
        value_list.append(raw_vol)
        _ = value_list.pop(0)     # to avoid print out
        time.sleep_us(300)  # wait for avoid power line noise (interval 1ms)
        time.sleep_ms(SENSOR_MEASUREMENT_TIMING)  # wait until sensor output is updated

    filterd_value = median_filter(value_list)
    estim_dist0 = 23.75 / (filterd_value - 0.125) - 0.42   # specification
    estim_dist1 = 23.36 / (filterd_value - 0.224) - 0.42    # local test
    estim_dist2 = 1 / (filterd_value * 0.04388 - 0.007506) - 0.42    # local test2
    print(filterd_value, estim_dist0, estim_dist1, estim_dist2)


measure_loop()
    
