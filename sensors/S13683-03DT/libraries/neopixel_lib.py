#
# NeoPixel driver
# some functions for control NeoPixel
#
from neopixel import NeoPixel

def neopixel_init(pin, pixcel_size):
    np = NeoPixel(pin, pixcel_size) 
    return np

def light_on(np, brightness=20):
    rgb_brightness = (int(brightness * 1.7), int(brightness * 1.0), int(brightness * 0.9))
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              

def light_off(np):
    for i in range(len(np)):
       np[i] = (00, 00, 00)
    np.write()              

def light_red(np, brightness=20):
    rgb_brightness = (brightness, 0 , 0)
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              

def light_blue(np, brightness=20):
    rgb_brightness = (0, 0 , brightness)
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              

def light_green(np, brightness=20):
    rgb_brightness = (0, brightness, 0)
    for i in range(len(np)):
       np[i] = rgb_brightness
    np.write()              

