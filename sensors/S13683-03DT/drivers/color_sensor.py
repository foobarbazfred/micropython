#
# sample code for Color Sensor
#  v0.01 (2025/3/22)
#  v0.02 (2025/3/23)    refactoring
#  v0.03 (2025/3/23)    Feature Update; white balanace
#

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
INTEGRATIN_TIME_LONG = 0b11        #  11:179.2ms
INTEGRATIN_TIME_SL_LONG = 0b10
INTEGRATIN_TIME_SL_SHORT = 0b01
INTEGRATIN_TIME_SHORT = 0b00

# default whilte balance
WHITE_BALANCE={'r' : 1788, 'g' : 2900,  'b' : 2819}


#LED_PIN : 0
#WB_SW : 1
#

LED_PIN = 0
WB_SW_PIN = 1



def init_sensor(i2c):
    set_control_reg(i2c, 0xe4)   # RESET,WAIT_MODE,MANUAL_SETTING_MODE
    set_manual_timing_reg(i2c, 0x0c,0x40)   #   Tint 00 , 546ms

def set_control_reg(i2c, data):
    bytes_data = bytes((data,))
    i2c.writeto_mem(I2C_ADDR, REG_CTRL, bytes_data)

def read_control_reg(i2c):
    return i2c.readfrom_mem(I2C_ADDR, REG_CTRL, 1)[0]


def set_manual_timing_reg(i2c, upper_byte, lower_byte):
    bytes_data = bytes((upper_byte, lower_byte))
    i2c.writeto_mem(I2C_ADDR, REG_MANUAL_TIMING, bytes_data)


#def rgb_read(i2c):
#    set_control_reg(i2c, 0x84)   # RESET,Operating mode, Low gain, ManualSetting
#    set_control_reg(i2c, 0x04)   # 
#    time.sleep_ms(546*4+100)
#    return read_rgb_regs(i2c)


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
    ctrl_params = HIGH_GAIN + INTEGRATIN_TIME_SL_LONG  # HIGH and 10 (22.4ms)
    set_control_reg(i2c, ctrl_params)  
    samples = []
    for _ in range(20):   #get 20 samples
        (raw_r, raw_g, raw_b, adjust) = read_rgb_regs(i2c)
        time.sleep_ms(200)     # wait 200msec
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


def median_filter(samples):
    key_value_list = {}
    for sample in samples:
       key = sample[3]
       key_value_list[key] = sample

    center_idx = int(len(key_value_list)/2)
    key_of_center_value = list(key_value_list.keys())[center_idx]
    return key_value_list[key_of_center_value]


def sensor_start(i2c ,np):

    global wb_mode
    np_light_on(np)    

    #set_control_reg(i2c, 0x89)   # RESET,High gain 1.4ms
    ctrl_params = 0x80 + HIGH_GAIN + INTEGRATIN_TIME_SL_LONG   # RESET,High gain
    set_control_reg(i2c, ctrl_params)  
    ctrl_params = HIGH_GAIN + INTEGRATIN_TIME_SL_LONG   # startsensing
    set_control_reg(i2c, ctrl_params)  

    while True:
        if wb_mode:
            update_white_balance(i2c)
            wb_mode = False
        #time.sleep_ms(179.2 * 5)
        time.sleep(1)
        (raw_r, raw_g, raw_b, adjust) = read_rgb_regs(i2c)
        print('-------------------------------------')
        print(f'raw:{raw_r}({raw_r:04x}), {raw_g}({raw_g:04x}), {raw_b}({raw_g:04x}) {adjust}({adjust:04x})')
        norm_r = raw_r / WHITE_BALANCE['r']
        norm_g = raw_g / WHITE_BALANCE['g']
        norm_b = raw_b / WHITE_BALANCE['b']
        print(f'norm: R: {norm_r}, G: {norm_g}, B: {norm_b}')
        (hue, sat, brt) = rgb2hsv(norm_r, norm_g, norm_b)
        print(f"Hue: {hue}, Sat: {sat}, Brt: {brt}")
        print(hue2cr(hue))
        if(brt > 1.5):
           print("wb!")

def rgb2hsv(r,g,b):
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


#hex(i2c.readfrom_mem(0x2a,0,1)[0])
##'0xe4'
#i2c.readfrom_mem(0x2a,0,3)
#i2c.readfrom_mem(0x2a,0,11)


#
#
#


np = None
def neopixel_init(pin):
    np = NeoPixel(pin, 20)   
    return np

def np_light_off(np):
    np[9] = (00, 00, 00)
    np[10] =   (00, 00, 00)
    np[11] =   (00, 00, 00)
    np[12] =   (00, 00, 00)
    np.write()              

def np_light_on(np,brightness=20):
    rgb_brightness = (brightness, brightness, brightness)
    np[9] = rgb_brightness
    np[10] =  rgb_brightness
    np[11] =  rgb_brightness
    np[12] =  rgb_brightness
    np.write()              

#
#
#

#
# https://zokeifile.musabi.ac.jp/%E8%89%B2%E7%9B%B8%E7%92%B0/
# Munsell Color Wheel

COLOR_WHEEL = ("5R", "10R", "5YR", "10YR", "5Y", "10Y", "5GY", "10GY", "5G", "10G", "5GB", "10GB", "5B", "10B", "5PB", "10PB", "5P", "10P", "5RP", "10RP")

def hue2cr(hue):
  if hue < 9 or hue > 350:
    idx = 0
  else:
    idx = int((hue - 9) / 18) + 1
  return COLOR_WHEEL[idx]


wb_mode = False
def wb_sw_handler(args):
    global wb_mode
    wb_mode = True

#
#
#
np = None
wb_sw = None
i2c = None

def main():

    global np
    global wb_sw
    global i2c

    # setup for white balance sw
    wb_sw = Pin(WB_SW_PIN, Pin.IN, Pin.PULL_UP)
    wb_sw.irq(handler=wb_sw_handler, trigger=Pin.IRQ_FALLING)

    # setup and turn on LED light
    pin = Pin(LED_PIN, Pin.OUT)   
    np = neopixel_init(pin)
    np_light_on(np)

    i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10_000) # OK??
    init_sensor(i2c)
    sensor_start(i2c,np)




main()


