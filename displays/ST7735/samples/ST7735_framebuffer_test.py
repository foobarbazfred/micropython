#
#  frame buffer test
#
import time
from machine import Pin
from machine import SPI
import framebuf

from st7735r import ST7735R


TFT_SPI_BAUD=800_0000   #800Kbps
TFT_SPI_MOSI=11
TFT_SPI_MISO=8
TFT_SPI_SCK=10

mosi  = Pin(TFT_SPI_MOSI, Pin.OUT)
miso  = Pin(TFT_SPI_MISO, Pin.OUT)
sck  = Pin(TFT_SPI_SCK, Pin.OUT)

TFT_DC=12
TFT_CS=13
TFT_RST=14

rst  = Pin(TFT_RST, Pin.OUT)
cs  = Pin(TFT_CS, Pin.OUT)
dc  = Pin(TFT_DC, Pin.OUT)

TFT_WIDTH=128
TFT_HEIGHT=160


spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )	# blue and green tab work
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(tft.COLOR_BLACK)


#
#

# byte swapped
COLOR_WHITE = 0xFFFF
COLOR_BLACK = 0x0000
COLOR_RED   = 0x00F8
COLOR_GREEN = 0xE007
COLOR_BLUE  = 0x1F00


W = 100   # max Width of LCD
H = 30   # max Height of LCD
(POS_X , POS_Y) = (10, 50)

# create frame buffer for RGB565 pixel and 30x30
b_ary = bytearray(W * H * 2)
fbuf = framebuf.FrameBuffer(b_ary, W, H, framebuf.RGB565)

fbuf.fill(COLOR_GREEN)
fbuf.text('MicroPython!', 8, int(H/3), COLOR_WHITE)
fbuf.hline(0, int(H/4) , W, COLOR_RED)     # x.y.w.c
fbuf.hline(0, int(H/4*3) , W, COLOR_RED) # x.y.w.c
fbuf.rect(0, 0, W, H, COLOR_BLUE)

tft._set_window(POS_X, POS_Y, POS_X + W - 1, POS_Y + H - 1)
tft.data(b_ary)
