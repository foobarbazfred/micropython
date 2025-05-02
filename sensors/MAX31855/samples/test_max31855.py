import time
from machine import Pin
from machine import SPI
from max31855 import MAX31855

SPI_CH0 = 0  # SPI Channel 0
GP_CLK = 2  # SPI0_CLK  : GP2 [4]
GP_MOSI = 3 # SPI0_MOSI : GP3 [5]
GP_MISO = 4 # SPI0_MISO : GP4 [6]
GP_CS = 5   # SPI CS    : GP5 [7]
SPI_CLK = 5_000_000  # SPI Clock 500KHz

#
# setup SPI and CS
#
spi = SPI(SPI_CH0, baudrate=SPI_CLK, polarity=0, phase=0, bits=8, sck=Pin(GP_CLK), mosi=Pin(GP_MOSI), miso=Pin(GP_MISO))
cs = Pin(GP_CS, Pin.OUT)

#
# initialize MAX31855
#
max31855 = MAX31855(spi, cs)

while True:
    tc_temp, int_temp, temp_NIST, status = max31855.get_temperature()
    print('--------------------')
    print(f'Thermocouple Temp: {tc_temp}')
    print(f'Internal Temp: {int_temp}')
    print(f'NIST Temp: {temp_NIST}')
    print(f'status: {status}')
    time.sleep(1)

