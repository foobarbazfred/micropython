#
# sample program for SD1306 Display
#
# repository of driver for SSD1306 Display Controller
# https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py
#

#
# if you did not installed the driver, please install as followings
# import mip
# mip.install('ssd1306')
#

from machine import I2C
from machine import Pin
from ssd1306  import SSD1306_I2C

DISP_I2C_ADDR = 0x3c
DISP_I2C_SCL = 1
DISP_I2C_SDA = 0
DISP_I2C_FREQ = 100_000  # 100KHz

DISP_WIDTH = 128
DISP_HEIGHT = 32

SSD1306_WHITE = 1
SSD1306_BLACK = 0

i2c = I2C(0, scl=Pin(DISP_I2C_SCL), sda=Pin(DISP_I2C_SDA), freq=DISP_I2C_FREQ)
disp_ssd1306 =  SSD1306_I2C(DISP_WIDTH, DISP_HEIGHT, i2c, addr=DISP_I2C_ADDR)

disp_ssd1306.fill(SSD1306_BLACK)
disp_ssd1306.rect(0,0, 128, 32, SSD1306_WHITE)
disp_ssd1306.text('Hello,', 10, 8, SSD1306_WHITE)
disp_ssd1306.text('  World!', 10, 18, SSD1306_WHITE)
disp_ssd1306.show()


