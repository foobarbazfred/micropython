#
#  Pulse rate monitor with MAX30100
#  V0.01 (2024/10/05)
#    modified:  changed current setting  of IR/RED LED 
#    https://github.com/devxplained/MAX3010x-Sensor-Library/blob/main/src/MAX30100.cpp
#    moving average N=10 (window size:10)
#  V0.02 (2025/5/6) refactor; create MAX30100 Driver
#  V0.03 (2025/5/6) refactor; define constants
#  V0.04 (2025/5/8) refine algorithm
#                   not invert graph
#  V0.05 (2025/5/8) refine algorithm
#                   change window size 10 -> 5 and change THRESHOLD
#  V0.06 (2025/5/8) refactor; rename variables 
#  V0.07 (2025/5/8) refactor; rename variables 
#  V0.08 (2025/5/10) Added new feature; LCD support.
#  V0.09 (2025/5/10) Modification: Reversed the LED brightness routine from 0-1 to 1-0.
#                  
#


import time
import math
from machine import Pin
from machine import I2C
from machine import PWM

from max30100 import MAX30100

DEV_ADDR = 0x57
VALID_DIFFERENCE_THRESHOLD = -30

MAX30100_I2C_0 = 0
MAX30100_I2C_SCL = 5  # Pin5
MAX30100_I2C_SDA = 4  # Pin4
MAX30100_I2C_FREQ = 100_000

from st7032 import ST7032LCD
LCD_I2C_1 = 1
LCD_I2C_SDA = 18  # Pin18
LCD_I2C_SCL = 19  # Pin19
LCD_I2C_FREQ = 10_000  # freq 10KHz

FEEDBACK_LED = 16  # Pin16



# threshold for Measurement is valid 
# any data must be larger than this value
MEASUREMENT_VALIDATION_THRESHOLD = 10000 

def set_LED_brightness(led, brightness):
    led.duty_u16(brightness)


def calc_pulse_rate(hr_sensor, led, lcd):

    hr_sensor.clear_ovfl_data()
    prev_ir = 0
    process_count = 0
    moving_ave_buffer = [0] * 5
    ir_raw_buffer = [0] * 100
    filtered_data = 0
    prev_tick = time.ticks_us()

    while True:
        # wait until HR_RDY:H 
        while True:
            intr = hr_sensor.read_interrupt_status()
            if intr & 0b0010_0000:  # HR_RDY
                break
            else:
                pass

        process_count += 1
        if process_count > 100_000:
            process_count = 0

        data = hr_sensor.read_FIFO_data_4B()
        ir = (data[0] << 8) + data[1]

        # calc differential
        diff = ir - prev_ir
        prev_ir = ir

        # add new data to queue (difference)
        moving_ave_buffer.pop(0)
        moving_ave_buffer.append(diff)

        # add new data to queue (raw data)
        ir_raw_buffer.pop(0)
        ir_raw_buffer.append(ir)

        #
        # notify a finger placement is correct or not by indicate with LED
        #
        if (process_count % 2) == 0:  # Reduce processing by half (50times/sec -> 25times/sec)
            max_val = max(ir_raw_buffer)
            min_val = min(ir_raw_buffer)
            mean_val = int(sum(ir_raw_buffer)/len(ir_raw_buffer))
            if min_val > MEASUREMENT_VALIDATION_THRESHOLD:   
                # blink LED only if in collect measuring
                brightness = int(0xffff * (1.0 - (max_val - ir) / (max_val - min_val)))
            else:
                # if error, then turn off LED
                brightness = 0
            set_LED_brightness(led, brightness)

        # 
        # calcurate Heart Rate
        # 

        # apply moving averate filter and get filtered data
        prev_filtered_data = filtered_data
        filtered_data = int(sum(moving_ave_buffer)/len(moving_ave_buffer))

        # check cross the threshold
        if filtered_data < VALID_DIFFERENCE_THRESHOLD and prev_filtered_data >= VALID_DIFFERENCE_THRESHOLD:

            # Prevent false detections by ensuring the value is valid.
            min_val = min(ir_raw_buffer)
            if  min_val > MEASUREMENT_VALIDATION_THRESHOLD:   
 
                # measure interval between cross point
                #print('-----------', end='') 
                current_tick = time.ticks_us()
                delta = time.ticks_diff(current_tick, prev_tick)
 
                # Calculate BPM using valid data
                bpm = int(60 * 1000 * 1000 / delta)
                if bpm >= 50 and bpm <= 220:   # display only if collect values.
                    message = f'heart rate: {bpm} BPM\nperiod: {int(delta/1000)} ms'
                    print(message)
                    message = f'HR: {bpm} BPM\nperiod: {int(delta/1000)} ms'
                    lcd.print(message,cls=True)
                else:                          # not display if abnormal values
                    print(f'heart rate: xxx, period: {int(delta/1000)} ms')
                prev_tick = current_tick
 
    return None




def main():

    #
    # device setup
    #

    # setup LCD
    lcd_i2c = I2C(LCD_I2C_1, scl = Pin(LCD_I2C_SCL), sda = Pin(LCD_I2C_SDA), freq = LCD_I2C_FREQ)
    lcd =  ST7032LCD(lcd_i2c)

    # feed back led
    led = PWM(Pin(FEEDBACK_LED), freq=500, duty_u16 = 0)
    
    # setup MAX30100
    i2c0 = I2C(MAX30100_I2C_0, scl=Pin(MAX30100_I2C_SCL), sda=Pin(MAX30100_I2C_SDA), freq=MAX30100_I2C_FREQ)  # 100KHz
    
    if DEV_ADDR in i2c0.scan():
        print('connection ok')
    else:
        print('Error! check device connection')
    
    hr_sensor = MAX30100(i2c0)
    hr_sensor.setup()
    
    print('pelase put your finger on sensor')
    lcd.print('please put your\nfinger on sensor')

    #
    #  calcurate plus rate
    #
    calc_pulse_rate(hr_sensor, led, lcd)
    

main()

#
# end of file
#
