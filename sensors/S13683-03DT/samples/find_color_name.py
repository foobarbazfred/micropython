#
# sample code for Color Sensor S13683-03DT
# find color name and display on LCD
#
#  v0.01 (2025/3/22)
#  v0.02 (2025/3/23)    refactoring
#  v0.03 (2025/3/23)    Feature Update; white balanace
#  v0.04 (2025/3/23)    Feature Update; identify  white color, black color
#  v0.05 (2025/3/30)    Feature Update; change COLOR LED RING (12 LEDS)
#  v0.06 (2025/4/6)     Feature Update; add color name, check facing target or not
#  v0.07 (2025/4/7)     Feature Update; check target is persistence or not
#                       bug fix:  wait time is not *3 but *4 (r,g,b,brightness)
#  v0.08 (2025/5/4)     change connect pins
#                       bug fix: median filter (not orderd)
#  v0.09 (2025/5/5)     modify color table
#  v0.10 (2025/5/5)     refactur; rewrite to class type
#

import time
from machine import Pin
from machine import I2C
from st7032 import ST7032LCD
from s13683_03dt import S13683_03DT

# load functions
import neopixel_lib
from color_lib import *

I2C_ADDR_S13683_03DT = 0x2a

# define register values for Color Sensor
HIGH_GAIN = 0b0000_1000
LOW_GAIN = 0x00
INTEGRATION_TIME_LONG = 0b11        #  11:179.2ms
INTEGRATION_TIME_SL_LONG = 0b10     #  10:22.4ms
INTEGRATION_TIME_SL_SHORT = 0b01    #  01:1.4ms 
INTEGRATION_TIME_SHORT = 0b00       #  00:87.5us

# The white balance RGB values are the maximum values measured 
# when a white sheet is placed in front of the color sensor.
WHITE_BALANCE = {'r': 7852, 'g': 8731, 'b': 7890}



#
# Pin Assign
#

PIN_NEOPIXEL = 0
SIZE_OF_NEOPIXEL = 12
PIN_WHITEBALANCE_SW = 1

PIN_COLOR_SENSOR_I2C_0 = 0
PIN_COLOR_SENSOR_I2C_SDA=4
PIN_COLOR_SENSOR_I2C_SCL=5
COLOR_SENSOR_I2C_FREQ = 100_000    # 100KHz


LCD_I2C_1 = 1
LCD_I2C_SDA = 18
LCD_I2C_SCL = 19
LCD_I2C_FREQ = 10_000  # freq 10KHz



# define constant for check not placing target or not
OPEN_BLIGHTNESS = 0.25

def update_white_balance(color_sensor):
    global  WHITE_BALANCE
    print('white balance start')
    print('put white paper on the color senser')
    time.sleep(1)  # wait for 1sec
    # set default params
    ctrl_params = HIGH_GAIN + INTEGRATION_TIME_SL_LONG  # HIGH and 10 (22.4ms)
    color_sensor.write_control_reg(ctrl_params)  
    samples = []
    for _ in range(5):   #get 5 samples
        (raw_r, raw_g, raw_b, adjust) = color_sensor.read_rgb_regs()
        #time.sleep_ms(int(179.2 * 4 ))     # wait 179.2 * 4
        time.sleep_ms(int(22.4 * 4 + 100))       # wait 22.4 * 4
        print(raw_r, raw_g, raw_b, adjust)
        samples.append((raw_r, raw_g, raw_b, adjust))
    center_value = median_filter(samples)
    print('end of white balance')
    print(WHITE_BALANCE)
    print('->')
    print(center_value)
    WHITE_BALANCE['r'] = center_value[0]
    WHITE_BALANCE['g'] = center_value[1]
    WHITE_BALANCE['b'] = center_value[2]


#
# find center value of sample data
# (sort by adjust value, and get center value )
#
def median_filter(samples):
    key_value_list = {}
    for sample in samples:
       key = sample[3]          # 3: adjust value in sampling data (r,g,b,adjust)
       key_value_list[key] = sample

    center_idx = int(len(key_value_list)/2)
    key_of_center_value = sorted(list(key_value_list.keys()))[center_idx]
    return key_value_list[key_of_center_value]

def identify_color(color_sensor, neopixel, lcd):

    global whiltebalance_mode
    global is_target_presence

    neopixel_lib.light_on(neopixel)    

    ctrl_params = 0x80 + HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # RESET,High gain
    color_sensor.write_control_reg(ctrl_params)  
    ctrl_params = HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # startsensing
    color_sensor.write_control_reg(ctrl_params)  

    while True:
        if whiltebalance_mode:
            update_white_balance(color_sensor)
            whiltebalance_mode = False
        time.sleep_ms(int(22.4 * 4 + 100))       # wait 22.4 * 4
        (raw_r, raw_g, raw_b, adjust) = color_sensor.read_rgb_regs()
        print('-------------------------------------')
        print(f'raw:{raw_r}({raw_r:04x}), {raw_g}({raw_g:04x}), {raw_b}({raw_g:04x}) {adjust}({adjust:04x})')
        norm_r = raw_r / WHITE_BALANCE['r']
        norm_g = raw_g / WHITE_BALANCE['g']
        norm_b = raw_b / WHITE_BALANCE['b']
        print(f'norm: R: {norm_r}, G: {norm_g}, B: {norm_b}')
        print(f'norm: R: {int(norm_r*255)}, G: {int(norm_g*255)}, B: {int(norm_b*255)}')
        (hue, sat, brt) = rgb2hsv(norm_r, norm_g, norm_b)
        print(f'Hue: {hue}, Sat: {sat}, Brt: {brt}')

        if brt < OPEN_BLIGHTNESS  and (not is_reflecting(color_sensor, neopixel, adjust)):   # if open (blightness of open)
              print('not facing')
              lcd.print('The object is\nnot placed.',cls=True)
              is_target_presence = False
              return
        else:
              color_name = hsv2color_name(hue,sat,brt)
              print(color_name)
              msg = f'color: {color_name}\nR:{int(norm_r*255):02X}, G:{int(norm_g*255):02X}, B:{int(norm_b*255):02X}'
              lcd.print(msg,cls=True)

        if(brt > 1.5):
              print('please adjust white balance, press the switch')
              lcd.print('Adjust the\nwhite balance.',cls=True)

        time.sleep(0.5)


#
# to determine whether the target is reflecting a light source
# (Blink white light assuming the target is placed in front of the sensor)
#
#   True ... target is reflecting a light
#   False ... target is not reflecting a light
#
REFLECT_THRESHOLD = 10
def is_reflecting(color_sensor, neopixel, prev_adjust):
    neopixel_lib.light_on(neopixel, brightness=10)      # set dimmer
    time.sleep_ms(int(22.4 * 4 + 200))       # wait 22.4 * 4
    (raw_r, raw_g, raw_b, adjust) = color_sensor.read_rgb_regs()
    neopixel_lib.light_on(neopixel)
    diff = abs(prev_adjust - adjust)
    if diff >= REFLECT_THRESHOLD:
         return True
    else:
         return False


CW_BLACK_LEVEL_BRIGHTNESS = 0.19
CW_WHITE_LEVEL_BRIGHTNESS = 0.8
CW_WHITE_LEVEL_SATURATION = 0.1

whiltebalance_mode = False
whitebalance_sw = None
def whitebalance_sw_handler(args):
    global whiltebalance_mode
    whiltebalance_mode = True

#
#
#

is_target_presence = False

# threshold for target is exists or not by judge color change

THRESHOLD_COLOR_DIFF = 50   

#
# Determine whether the object is placed in front of the sensor
# return value with changing color of LED light
# (change the color of LED assuming the target is not placed in front of the sensor
# To avoid strong light blinking, Use this test function when the target is not placed 
#
#   True ...   object is placed in front of the sensor
#   False ...  object is not placed in front of the sensor
#
#
def check_target_presence(color_sensor, neopixel):
    while True:
       # turn on green
       neopixel_lib.light_green(neopixel, brightness=2)
       time.sleep(0.5)   # Select a suitable value intuitively
       (raw_r, raw_g, raw_b, adjust_light) = color_sensor.read_rgb_regs()
       norm_r = raw_r / WHITE_BALANCE['r']
       norm_g = raw_g / WHITE_BALANCE['g']
       norm_b = raw_b / WHITE_BALANCE['b']
       (hue_in_g, sat, brt) = rgb2hsv(norm_r, norm_g, norm_b)

       # turn on blue
       neopixel_lib.light_blue(neopixel, brightness=8)
       time.sleep(0.5)  # Select a suitable value intuitively
       (raw_r, raw_g, raw_b, adjust_light) = color_sensor.read_rgb_regs()
       norm_r = raw_r / WHITE_BALANCE['r']
       norm_g = raw_g / WHITE_BALANCE['g']
       norm_b = raw_b / WHITE_BALANCE['b']
       (hue_in_b, sat, brt) = rgb2hsv(norm_r, norm_g, norm_b)
       diff = abs(hue_in_g - hue_in_b)
       #print(f'diff: {diff}')
       if diff > THRESHOLD_COLOR_DIFF:
           return True
       else:
           return False


def main():

    global whitebalance_sw
    global is_target_presence

    # setup for white balance sw
    whitebalance_sw = Pin(PIN_WHITEBALANCE_SW, Pin.IN, Pin.PULL_UP)
    whitebalance_sw.irq(handler=whitebalance_sw_handler, trigger=Pin.IRQ_FALLING)

    # setup and turn on LED light
    neopixel = neopixel_lib.neopixel_init(Pin(PIN_NEOPIXEL), SIZE_OF_NEOPIXEL)     # 12 LED RING
    neopixel_lib.light_on(neopixel)

    # setup for LCD
    lcd_i2c = I2C(LCD_I2C_1, scl=Pin(LCD_I2C_SCL), sda=Pin(LCD_I2C_SDA), freq=LCD_I2C_FREQ)
    lcd =  ST7032LCD(lcd_i2c)

    # setup for color sensor
    i2c0 = I2C(PIN_COLOR_SENSOR_I2C_0, scl=Pin(PIN_COLOR_SENSOR_I2C_SCL), sda=Pin(PIN_COLOR_SENSOR_I2C_SDA), freq=COLOR_SENSOR_I2C_FREQ) 
    # connection check
    if I2C_ADDR_S13683_03DT in i2c0.scan():
         pass
    else:
         print('connection of Color sensor is error')
         print('pease check connection')
         sys.exit()

    color_sensor = S13683_03DT(i2c0)

    while True:
        if is_target_presence:
             identify_color(color_sensor, neopixel, lcd)
        else:
             is_target_presence = check_target_presence(color_sensor, neopixel)
             if not is_target_presence:
                print('Place the target in front of the sensor.')
                lcd.print('Place object\non the sensor.', cls=True)

main()


#
# end of file
#
