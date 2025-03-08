import time
from machine import Pin, SPI
from max31855 import MAX31855

SPI_CH = 0  # SPI0
GP_CLK = 2  # SPI0_CLK  : GP2 [4]
GP_MOSI = 3 # SPI0_MOSI : GP3 [5]
GP_MISO = 4 # SPI0_MISO : GP4 [6]
GP_CS = 5   # SPI CS    : GP5 [7]
SPI_CLK = 5_000_000  # SPI Clock 50KHz

#
# setup SPI and CS
#
spi = SPI(SPI_CH, baudrate=SPI_CLK, polarity=0, phase=0, bits=8, sck=Pin(GP_CLK), mosi=Pin(GP_MOSI), miso=Pin(GP_MISO))
cs = Pin(GP_CS, Pin.OUT)

#
# initialize MAX31855
#
max31855 = MAX31855(spi, cs)

while True:
    (tc_temp, int_temp, status) = max31855.get_temperature()
    print(tc_temp, status)
    time.sleep(1)
    
