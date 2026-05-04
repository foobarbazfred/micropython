#
# Arducam and LCD Demo
# file: arducam_lcd_demo.py
# v0.0.2 (2026/04/30)
# v0.0.3 (2026/05/01)


#
# test program for Graphic Display with ST7735 Driver 
# original source is https://github.com/mcauser/micropython-st7735/blob/master/test.py
#

# GP8  SPI1 Rx
# GP9  SPI1 CSn
# GP10 SPI1 SCK
# GP11 SPI1 TX
# GP12 A0 
# GP13 CS
# GP14 RESET

import time
from machine import Pin
from machine import SPI
from st7735r import ST7735R

#
# Color defines (RGB565)
#
COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF

#
# LCD size defines (128 x 160)
#
TFT_WIDTH = 128
TFT_HEIGHT = 160

#
# Pin assigns
#
TFT_SPI_BAUD = 800_0000   #800Kbps
TFT_SPI_MOSI = 11
TFT_SPI_MISO = 8
TFT_SPI_SCK = 10

TFT_DC = 12
TFT_CS = 13
TFT_RST = 14

mosi  = Pin(TFT_SPI_MOSI, Pin.OUT)
miso  = Pin(TFT_SPI_MISO, Pin.OUT)
sck  = Pin(TFT_SPI_SCK, Pin.OUT)

rst  = Pin(TFT_RST, Pin.OUT)
cs  = Pin(TFT_CS, Pin.OUT)
dc  = Pin(TFT_DC, Pin.OUT)

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )

#
#  create and initialize tft instance
#
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.rotate(1)   # rotate screen 90 degrees
tft.fill(COLOR_BLACK)


#
#  setup Arducam(OV5642)
#
#

from machine import I2C
from ov5642 import OV5642

ov5642i2c = I2C(scl=Pin(5), sda=Pin(4), freq=9600)
CAM_PIN_CS = 1
fifo_cs = Pin(CAM_PIN_CS, Pin.OUT)

SPI0_BAUDRATE = 7_000_000   # Datasheet max: 8 MHz (running at half speed for stability)
SPI0_MOSI = 3
SPI0_MISO = 0
SPI0_SCK = 2
fifo_spi = SPI(0,SPI0_BAUDRATE,sck=Pin(SPI0_SCK), mosi=Pin(SPI0_MOSI), miso=Pin(SPI0_MISO))

ardu = OV5642(ov5642i2c, fifo_spi, fifo_cs)

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 128
BYTEPERPIX = 2  # RGB565

#
#  take picture by Arducam and display on LCD
#
#

import gc
gc.collect()
buf = bytearray(SCREEN_WIDTH * SCREEN_HEIGHT * BYTEPERPIX)

def show_image():
    global buf
    ardu.read_pixels(buf)
    tft._set_window(0, 0, SCREEN_WIDTH - 1, SCREEN_WIDTH - 1)
    tft.data(buf)

def camera_demo():
    prev_time=time.ticks_ms()
    while True:
        ardu.fifo.clear_done_flag()       
        ardu.fifo.start_capture_and_wait()
        show_image()
        current_time = time.ticks_ms()
        print('Processing time:', time.ticks_diff(time.ticks_ms(), prev_time),' ms')
        prev_time = current_time

camera_demo()


#
#
#




