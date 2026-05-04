#
# use library:
#  import mip
#  mip.install('https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/st7735r.py')
#
# if you draw text, install terminalfont as followings
#  import mip
#  mip.install('https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/terminalfont.py')
#
#

import time
from machine import Pin
from machine import SPI
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

COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_RED = 0xF800
COLOR_GREEN = 0x07E0
COLOR_BLUE = 0x001F
COLOR_CYAN = 0x07FF
COLOR_MAGENTA = 0xF81F


cyan = 0x07FF
magenta = 0xF81F
yellow = 0xFFE0

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )	# blue and green tab work
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(COLOR_BLACK)

#tft.fill(COLOR_WHITE)


for _ in range(3):
    for color in (COLOR_RED, COLOR_GREEN, COLOR_BLUE):
          tft.fill(color)
          time.sleep(1)

tft.fill(COLOR_BLACK)
tft.rect_outline(0, 0, TFT_WIDTH, TFT_HEIGHT, COLOR_BLUE)
tft.line(0, 0, TFT_WIDTH, TFT_HEIGHT, COLOR_RED)
tft.line(TFT_WIDTH, 0, 0, TFT_HEIGHT, COLOR_GREEN)


if TFT_WIDTH < TFT_HEIGHT:
   radius = int(TFT_WIDTH/2)
else:
   radius = int(TFT_HEIGHT/2)
tft.circle_outline(int(TFT_WIDTH/2),int(TFT_HEIGHT/2),radius,COLOR_CYAN)
tft.line(10, 10, int(TFT_WIDTH/2), int(TFT_HEIGHT/2), COLOR_RED)


#
# draw text
#
import terminalfont

(pos_x, pos_y) = ( int(TFT_WIDTH/4), int(TFT_HEIGHT/5))
tft.text(pos_x, pos_y, 'Hello,', terminalfont, COLOR_WHITE, size=1)
tft.text(pos_x + 10, pos_y + 10, 'World!!', terminalfont, COLOR_WHITE, size=1)

#
# framebuffer test
#
import framebuf

# define of frame buffer size
W = 100  # Width of frame buffer
H = 30   # Height of frame buffer

# create frame buffer for RGB565, pixel(100 x 30)
b_ary = bytearray(W * H * 2)
fbuf = framebuf.FrameBuffer(b_ary, W, H, framebuf.RGB565)

# draw graphics and text into frame buffer
fbuf.fill(0)
fbuf.rect(0,0,W,H,0x00ff,False)
fbuf.text('MicroPython!', 2, 10 , 0xff00)

# define draing position in LCD
(POS_X , POS_Y) = (10, 50)

# show contents of framebuffer to LCD
tft._set_window(POS_X, POS_Y, POS_X + W - 1,POS_Y + H - 1)
tft.data(b_ary)





#
# MEMO
#


#https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/st7735r.py
#https://github.com/mcauser/micropython-st7735/tree/master

# GP8  SPI1 Rx
# GP9  SPI1 CSn
# GP10 SPI1 SCK
# GP11 SPI1 TX
# GP12 A0 
# GP13 CS
# GP14 RESET
