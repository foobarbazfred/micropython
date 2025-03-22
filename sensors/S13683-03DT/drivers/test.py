#
# sample code for Color Sensor
#  v0.01 (2025/3/22)
#
import time
from machine import Pin
from machine import I2C
from st7032 import ST7032LCD

i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10000) # OK??

I2C_ADDR=0x2a
REG_CTRL=0x00
REG_MANUAL_TIMING = 0x01
REG_RGB_SENSOR = 0x03
RGB_SENSOR_LENGTH = 8

HIGH_GAIN = 0x08
LOW_GAIN = 0x00
INTEGRATIN_TIME_LONG = 0b11        #  11:179.2ms
INTEGRATIN_TIME_SL_LONG = 0b10
INTEGRATIN_TIME_SL_SHORT = 0b01
INTEGRATIN_TIME_SHORT = 0b00

WHITE_BALANCE={'r':1788, 'g':2900,  'b':2819}

def set_control_reg(data):
    bytes_data = bytes((data,))
    i2c.writeto_mem(I2C_ADDR, REG_CTRL, bytes_data)

def set_manual_timing_reg(upper_byte, lower_byte):
    bytes_data = bytes((upper_byte, lower_byte))
    i2c.writeto_mem(I2C_ADDR, REG_MANUAL_TIMING, bytes_data)

def read_rgb_regs():
    data = i2c.readfrom_mem(I2C_ADDR, REG_RGB_SENSOR, RGB_SENSOR_LENGTH)
    r = (data[0] << 8) + data[1]
    g = (data[2] << 8) + data[3]
    b = (data[4] << 8) + data[5]
    adj = (data[6] << 8) + data[7]
    return (r, g, b, adj)

def init_sensor():
    set_control_reg(0xe4)   # RESET,WAIT_MODE,MANUAL_SETTING_MODE
    set_manual_timing_reg(0x0c,0x40)   #   Tint 00 , 546ms

def sensor_start():
    color_led_on(np)    
    #set_control_reg(0x89)   # RESET,High gain 1.4ms
    set_control_reg(0x80 + HIGH_GAIN + INTEGRATIN_TIME_SL_LONG)   # RESET,High gain
    set_control_reg(HIGH_GAIN + INTEGRATIN_TIME_SL_LONG)   # startsensing
    while True:
        #time.sleep_ms(179.2 * 5)
        time.sleep(1)
        (raw_r,raw_g,raw_b,c) = read_rgb_regs()
        print(raw_r,raw_g,raw_b,c)
        r = raw_r / WHITE_BALANCE['r']
        g = raw_g / WHITE_BALANCE['g']
        b = raw_b / WHITE_BALANCE['b']
        print(r,g,b)
        (h, s, b) = rgb2hsv(r,g,b)
        print(h,s,b)
        print(hsb2color(h))
        print(hue2cr(h))



def rgb_read():
    set_control_reg(0x84)   # RESET,Operating mode, Low gain, ManualSetting
    set_control_reg(0x04)   # 
    time.sleep_ms(546*4+100)
    return read_rgb_regs()

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





from machine import Pin
from neopixel import NeoPixel

np = None
def color_led_init():
    pin = Pin(0, Pin.OUT)   
    np = NeoPixel(pin, 20)   
    return np

def color_led_off(np):
    np[9] = (00, 00, 00)
    np[10] =   (00, 00, 00)
    np[11] =   (00, 00, 00)
    np[12] =   (00, 00, 00)
    np.write()              

def color_led_on(np):
    np[9] = (20, 20, 20)
    np[10] = (20, 20, 20)
    np[11] = (20, 20, 20)
    np[12] = (20, 20, 20)
    np.write()              

#
#
#

#
# https://zokeifile.musabi.ac.jp/%E8%89%B2%E7%9B%B8%E7%92%B0/
# マンセル色相環

COLOR_RING = ("5R", "10R", "5YR", "10YR", "5Y", "10Y", "5GY", "10GY", "5G", "10G", "5GB", "10GB", "5B", "10B", "5PB", "10PB", "5P", "10P", "5RP", "10RP")

def hue2cr(h):
  if h < 9 or h > 350:
    idx = 0
  else:
    idx = int((h-9)/18) + 1
  return COLOR_RING[idx]


np = color_led_init()
color_led_on(np)

init_sensor()
sensor_start()




#  def hsb2color(h):
#     color = None
#     if h < 50:
#          color = 'red'
#     elif h < 80:
#          color = 'yello'
#     elif h < 140:
#          color = 'green'
#     elif h < 220:
#          color = 'cyan'
#     elif h < 260:
#          color = 'blue'
#     elif h < 300:
#          color = 'magenta'
#     else:
#          color = 'red'
#     return color
#  
#  
#  
#  
#  
#  
#  #
#  #
