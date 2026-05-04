#
# use library:
#  import mip
#  mip.install('https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/st7735r.py')
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

# tft.COLOR_BLACK     
# tft.COLOR_WHITE     
# tft.COLOR_RED       
# tft.COLOR_BLUE
# tft.COLOR_GREEN     
# tft.COLOR_CYAN      
# tft.COLOR_MAGENTA   
# tft.COLOR_YELLOW

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )	# blue and green tab work
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(tft.COLOR_BLACK)

for _ in range(3):
    for color in (tft.COLOR_RED, tft.COLOR_GREEN, tft.COLOR_BLUE, tft.COLOR_YELLOW):
          tft.fill(color)
          time.sleep(0.5)

tft.fill(tft.COLOR_BLACK)
tft.rect_outline(0, 0, TFT_WIDTH, TFT_HEIGHT, tft.COLOR_BLUE)
tft.line(0, 0, TFT_WIDTH, TFT_HEIGHT, tft.COLOR_RED)
tft.line(TFT_WIDTH, 0, 0, TFT_HEIGHT, tft.COLOR_GREEN)


if TFT_WIDTH < TFT_HEIGHT:
   radius = int(TFT_WIDTH/2)
else:
   radius = int(TFT_HEIGHT/2)
tft.circle_outline(int(TFT_WIDTH/2),int(TFT_HEIGHT/2),radius,tft.COLOR_CYAN)
tft.line(10, 10, int(TFT_WIDTH/2), int(TFT_HEIGHT/2), tft.COLOR_RED)

#
#
#
