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
    #set_control_reg(0x89)   # RESET,High gain 1.4ms
    set_control_reg(0x8b)   # RESET,High gain 11:179.2ms
    set_control_reg(0x0b)   # start sensing
    while True:
        #time.sleep_ms(179.2 * 5)
        time.sleep(0.5)
        (r,g,b,c) = read_rgb_regs()
        print(r,g,b,c)
        (h, s, b) = rgb2hsv(r,g,b)
        print(h,s,b)
        print(hsb2color(h))


def rgb_read():
    set_control_reg(0x84)   # RESET,Operating mode, Low gain, ManualSetting
    set_control_reg(0x04)   # 
    time.sleep_ms(546*4+100)
    return read_rgb_regs()

def rgb2hsv(r,g,b):
    max_val = max((r,g,b))
    min_val = min((r,g,b))

    if max_val == min_val:
       return None

    if min_val == b:
         h = 60 * (g - r)/(max_val - min_val) + 60
    elif min_val == r:
         h = 60 * (b - g)/(max_val - min_val) + 180
    elif min_val == g:
         h = 60 * (r - b)/(max_val - min_val) + 300
    else:
         h = None

    s = (max_val - min_val)/max_val
    v = max_val
    
    return (h, s, v)



def hsb2color(h):
   color = None
   if h < 50:
        color = 'red'
   elif h < 80:
        color = 'yello'
   elif h < 140:
        color = 'green'
   elif h < 220:
        color = 'cyan'
   elif h < 260:
        color = 'blue'
   elif h < 300:
        color = 'magenta'
   return color

#hex(i2c.readfrom_mem(0x2a,0,1)[0])
##'0xe4'
#i2c.readfrom_mem(0x2a,0,3)
#i2c.readfrom_mem(0x2a,0,11)



init_sensor()
sensor_start()




#
#
#