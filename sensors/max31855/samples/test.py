import time
from machine import Pin, SPI
from max31855 import MAX31855

SPI_CH = 0  # SPI0
GP_CLK = 2  # SPI0_CLK : Pin 2
GP_MOSI = 3 # SPI0_MOSI : Pin 3
GP_MISO = 4 # SPI0_MISO : Pin 4
GP_CS = 5   # SPI CS : Pin 2

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

# >>> spi
# SPI(0, baudrate=4807692, polarity=0, phase=0, bits=8, sck=2, mosi=3, miso=4)
# >>> cs
# Pin(GPIO5, mode=OUT)

#cs.high()
#cs.low()
#spi.read(4)
#b'\x00\x00\x03\x00'

#data = bytes((0x1,0x4,0xf,0xa0))
#buf = bytearray(4)  # 16bit width buffer
#data = bytes((0x1,0x4,0xf,0xa0))
#buf[3] = 0x01
#buf[2] = 0x04
#buf[1] = 0x0f
#buf[0] = 0xa0



