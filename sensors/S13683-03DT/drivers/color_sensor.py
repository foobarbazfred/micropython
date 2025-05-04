#
# sample code for Color Sensor
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

import time
from machine import Pin
from machine import I2C
from st7032 import ST7032LCD

#
# for neopixel
#
from neopixel import NeoPixel


I2C_ADDR=0x2a
REG_CTRL=0x00
REG_MANUAL_TIMING = 0x01
REG_RGB_SENSOR = 0x03
RGB_SENSOR_LENGTH = 8

CTRL_ADC_RESET     = 0b1000_0000
CTRL_ADC_START     = 0b0000_0000
CTRL_SLEEP_MODE    = 0b0100_0000
CTRL_OPERATIN_MODE = 0b0000_0000
CTRL_SLEEP_MONITOR_BIT  = 0b0010_0000


CTRL_INTEG_MAN_MODE  = 0b0000_0100
CTRL_INTEG_FIX_MODE  = 0b0000_0000

HIGH_GAIN = 0b0000_1000
LOW_GAIN = 0x00
INTEGRATION_TIME_LONG = 0b11        #  11:179.2ms
INTEGRATION_TIME_SL_LONG = 0b10     #  10:22.4ms
INTEGRATION_TIME_SL_SHORT = 0b01    #  01:1.4ms 
INTEGRATION_TIME_SHORT = 0b00       #  00:87.5us

# default whilte balance (max value when white paper is set)
WHITE_BALANCE = {'r': 8025, 'b': 8598, 'g': 9049}
#{'g': 8846, 'b': 8268, 'r': 7769}
#{'r': 6221, 'g': 7484, 'b': 6792, }
#{'r': 5725, 'g': 6345, 'b': 5894, }

#LED_PIN : 0
#WB_SW : 1
#

LED_PIN = 0
WB_SW_PIN = 1

OPEN_BLIGHTNESS = 0.20


def init_sensor(i2c):
    set_control_reg(i2c, 0xe4)   # RESET,WAIT_MODE,MANUAL_SETTING_MODE
    set_manual_timing_reg(i2c, 0x0c,0x40)   #   Tint 00 , 546ms

def setup_sensor(i2c):
    ctrl_params = 0x80 + HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # RESET,High gain
    set_control_reg(i2c, ctrl_params)  
    ctrl_params = HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # startsensing
    set_control_reg(i2c, ctrl_params)  



def set_control_reg(i2c, data):
    bytes_data = bytes((data,))
    i2c.writeto_mem(I2C_ADDR, REG_CTRL, bytes_data)

def read_control_reg(i2c):
    return i2c.readfrom_mem(I2C_ADDR, REG_CTRL, 1)[0]

def set_manual_timing_reg(i2c, upper_byte, lower_byte):
    bytes_data = bytes((upper_byte, lower_byte))
    i2c.writeto_mem(I2C_ADDR, REG_MANUAL_TIMING, bytes_data)


def read_rgb_regs(i2c):
    data = i2c.readfrom_mem(I2C_ADDR, REG_RGB_SENSOR, RGB_SENSOR_LENGTH)
    r = (data[0] << 8) + data[1]
    g = (data[2] << 8) + data[3]
    b = (data[4] << 8) + data[5]
    adjust = (data[6] << 8) + data[7]
    return (r, g, b, adjust)


def update_white_balance(i2c):
    global  WHITE_BALANCE
    print('white balance start')
    print('put white paper on the color senser')
    time.sleep(1)  # wait for 1sec
    # set default params
    ctrl_params = HIGH_GAIN + INTEGRATION_TIME_SL_LONG  # HIGH and 10 (22.4ms)
    set_control_reg(i2c, ctrl_params)  
    samples = []
    for _ in range(5):   #get 5 samples
        (raw_r, raw_g, raw_b, adjust) = read_rgb_regs(i2c)
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
    key_of_center_value = sort(list(key_value_list.keys()))[center_idx]
    return key_value_list[key_of_center_value]


def sensor_start(i2c, np):

    global wb_mode
    global is_target_presence

    np_light_on(np)    

    #set_control_reg(i2c, 0x89)   # RESET,High gain 1.4ms
    ctrl_params = 0x80 + HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # RESET,High gain
    set_control_reg(i2c, ctrl_params)  
    ctrl_params = HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # startsensing
    set_control_reg(i2c, ctrl_params)  

    while True:
        if wb_mode:
            update_white_balance(i2c)
            wb_mode = False
        #time.sleep_ms(int(179.2 * 4 + 100.0))
        time.sleep_ms(int(22.4 * 4 + 100))       # wait 22.4 * 4
        (raw_r, raw_g, raw_b, adjust) = read_rgb_regs(i2c)
        print('-------------------------------------')
        print(f'raw:{raw_r}({raw_r:04x}), {raw_g}({raw_g:04x}), {raw_b}({raw_g:04x}) {adjust}({adjust:04x})')
        norm_r = raw_r / WHITE_BALANCE['r']
        norm_g = raw_g / WHITE_BALANCE['g']
        norm_b = raw_b / WHITE_BALANCE['b']
        print(f'norm: R: {norm_r}, G: {norm_g}, B: {norm_b}')
        print(f'norm: R: {int(norm_r*255)}, G: {int(norm_g*255)}, B: {int(norm_b*255)}')
        (hue, sat, brt) = rgb2hsb(norm_r, norm_g, norm_b)
        print(f"Hue: {hue}, Sat: {sat}, Brt: {brt}")

        if brt < OPEN_BLIGHTNESS  and (not is_reflection(i2c, adjust)):   # if open (blightness of open)
              print('not facing')
              is_target_presence = False
              return
        else:
              print(hsb2cw(hue,sat,brt))

        if(brt > 1.5):
           print("please set WB")

        time.sleep(0.5)

#
# check reflection
#
REFLECT_THRESHOLD = 10
def is_reflection(i2c, prev_adjust):
    np_light_on(np, brightness=10)      # set dimmer
    #time.sleep_ms(int(179.2 * 4 ))     # wait 179.2 * 4
    #time.sleep_ms(int(22.4 * 4 + 100))       # wait 22.4 * 4
    time.sleep_ms(int(22.4 * 4 + 200))       # wait 22.4 * 4
    (raw_r, raw_g, raw_b, adjust) = read_rgb_regs(i2c)
    np_light_on(np)
    diff = abs(prev_adjust - adjust)
    if diff >= REFLECT_THRESHOLD:
         return True
    else:
         return False


def rgb2hsb(r,g,b):
    max_val = max((r,g,b))
    min_val = min((r,g,b))

    if max_val == min_val:
       print('Error, max_val == min_val')
       return None

    if min_val == b:
         h = 60 * (g - r)/(max_val - min_val) + 60
    elif min_val == r:
         h = 60 * (b - g)/(max_val - min_val) + 180
    elif min_val == g:
         h = 60 * (r - b)/(max_val - min_val) + 300
    else:
         print('internal Error')
         h = None

    s = (max_val - min_val)/max_val
    v = max_val
    
    return (h, s, v)



#
#
#


np = None
def neopixel_init(pin):
    np = NeoPixel(pin, 12)    # 12 LED RING
    return np

def np_light_on(np, brightness=20):
    rgb_brightness = (int(brightness * 1.7), int(brightness * 1.0), int(brightness * 0.9))
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              


def np_light_off(np):
    for i in range(len(np)):
       np[i] = (00, 00, 00)
    np.write()              

#
#
#

#
# https://zokeifile.musabi.ac.jp/%E8%89%B2%E7%9B%B8%E7%92%B0/
# Munsell Color Wheel

CW_BLACK_LEVEL_BRIGHTNESS = 0.10
CW_WHITE_LEVEL_BRIGHTNESS = 0.8
CW_WHITE_LEVEL_SATURATION = 0.1

COLOR_WHEEL = ( "5R", "10R", "5YR", "10YR", "5Y", "10Y", "5GY", "10GY", "5G", "10G", "5BG", "10BG", "5B", "10B", "5PB", "10PB", "5P", "10P", "5RP", "10RP" )

COLOR_NAME = { 'R' : 'aka', 'YR' : 'daidai', 'Y' : 'ki', 'GY' : 'kimidori', 'G' : 'midori',
               'BG' : 'aomidori','G' : 'midori','B' : 'ao','PB' : 'aomurasaki','p' : 'murasaki',
               'RP' : 'akamurasaki' }


  
#h=360-10
#new_h = h + int(360 / len(COLOR_WHEEL) / 2)
#if new_h >= 360:
#   new_h -= 360
#idx = int(new_h / (360 / len(COLOR_WHEEL)))
#COLOR_WHEEL[idx]





#
# convert (h, s, b) to color name
#
def hsb2cw(h, s, b):
  new_h = h + int(360 / len(COLOR_WHEEL) / 2)
  if new_h >= 360:
     new_h -= 360
  idx = int(new_h / (360 / len(COLOR_WHEEL)))
  color_name = COLOR_WHEEL[idx]
  if b < CW_BLACK_LEVEL_BRIGHTNESS:     # if brightness is lower than 0.1 then black
     return('BK')
  if s < CW_WHITE_LEVEL_SATURATION  and b > CW_WHITE_LEVEL_BRIGHTNESS:
     return(f'HW')
  return color_name

#
# convert color_id to color name
#
def get_color_name(color_id):
    stripped_color_id = re.sub('[0-9]*', '', color_id)  # remove number from color_id
    if stripped_color_id in COLOR_NAME:
        return COLOR_NAME[stripped_color_id]
    else:
        return None


wb_mode = False
def wb_sw_handler(args):
    global wb_mode
    wb_mode = True

#
#
#
np = None
wb_sw = None
i2c0 = None

is_target_presence = False

def main():

    global np
    global wb_sw
    global i2c0
    global is_target_presence

    # setup for white balance sw
    wb_sw = Pin(WB_SW_PIN, Pin.IN, Pin.PULL_UP)
    wb_sw.irq(handler=wb_sw_handler, trigger=Pin.IRQ_FALLING)

    # setup and turn on LED light
    pin = Pin(LED_PIN, Pin.OUT)   
    np = neopixel_init(pin)
    np_light_on(np)

    i2c0 = I2C(0, scl=Pin(5), sda=Pin(4), freq=100_000)   # 100K
    init_sensor(i2c0)
    setup_sensor(i2c0)

    while True:
        if is_target_presence:
             sensor_start(i2c0,np)
        else:
             is_target_presence = check_target_presence(i2c0)
             if not is_target_presence:
                print('Please place the object you want to examine')


def np_light_red(np, brightness=20):
    rgb_brightness = (brightness, 0 , 0)
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              


def np_light_blue(np, brightness=20):
    rgb_brightness = (0, 0 , brightness)
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              

def np_light_green(np, brightness=20):
    rgb_brightness = (0, brightness, 0)
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              


THRESHOLD_COLOR_DIFF = 50

def check_target_presence(i2c):
    while True:
       # turn on green
       np_light_green(np, brightness=2)
       time.sleep(0.5)   # Select a suitable value intuitively
       (raw_r, raw_g, raw_b, adjust_light) = read_rgb_regs(i2c)
       norm_r = raw_r / WHITE_BALANCE['r']
       norm_g = raw_g / WHITE_BALANCE['g']
       norm_b = raw_b / WHITE_BALANCE['b']
       (hue_in_g, sat, brt) = rgb2hsb(norm_r, norm_g, norm_b)

       # turn on blue
       np_light_blue(np, brightness=8)
       time.sleep(0.5)  # Select a suitable value intuitively
       (raw_r, raw_g, raw_b, adjust_light) = read_rgb_regs(i2c)
       norm_r = raw_r / WHITE_BALANCE['r']
       norm_g = raw_g / WHITE_BALANCE['g']
       norm_b = raw_b / WHITE_BALANCE['b']
       (hue_in_b, sat, brt) = rgb2hsb(norm_r, norm_g, norm_b)
       diff = abs(hue_in_g - hue_in_b)
       #print(f'diff: {diff}')
       if diff > THRESHOLD_COLOR_DIFF:
           return True
       else:
           return False


main()


#
# end of file
#
