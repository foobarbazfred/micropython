#
# draw text test
# to execute, please install libraries
#  (1) ST7735 Driver
#  (2) font data (terminalfont.py)
#      import mip
#      mip.install('https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/terminalfont.py')
#
#
import time
from machine import Pin
from machine import SPI
from st7735r import ST7735R
import terminalfont

TFT_SPI_BAUD = 800_0000   #800Kbps
TFT_SPI_MOSI = 11
TFT_SPI_MISO = 8
TFT_SPI_SCK = 10

mosi  = Pin(TFT_SPI_MOSI, Pin.OUT)
miso  = Pin(TFT_SPI_MISO, Pin.OUT)
sck  = Pin(TFT_SPI_SCK, Pin.OUT)

TFT_DC = 12
TFT_CS = 13
TFT_RST = 14

rst  = Pin(TFT_RST, Pin.OUT)
cs  = Pin(TFT_CS, Pin.OUT)
dc  = Pin(TFT_DC, Pin.OUT)

TFT_WIDTH=128
TFT_HEIGHT=160

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck)
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(tft.COLOR_BLACK)

(pos_x, pos_y) = (int(TFT_WIDTH/4), int(TFT_HEIGHT/5))
tft.text(pos_x, pos_y, 'Hello,', terminalfont, tft.COLOR_WHITE, size=1)
tft.text(pos_x + 10, pos_y + 10, 'World!!', terminalfont, tft.COLOR_WHITE, size=1)

#
#
