#
# test program for MAX31855
#
import time
from machine import Pin
from machine import SPI
from max31855 import MAX31855

SPI_CH0 = 0  # SPI Channel 0
SPI_CLK = 2  # SPI0_CLK  : GP2 [4]
SPI_MOSI = 3 # SPI0_MOSI : GP3 [5]
SPI_MISO = 4 # SPI0_MISO : GP4 [6]
SPI_CS = 5   # SPI CS    : GP5 [7]
SPI_FREQ = 500_000  # SPI Clock 500KHz

# for setup LCD
from machine import I2C
from st7032 import ST7032LCD

# pin assign for LCD
I2C_CH1 = 1
I2C_SCL = 19
I2C_SDA = 18
I2C_FREQ = 10_000   # I2C clock; 10KHz

def main():

    #
    # setup MAX31855
    #
    spi = SPI(SPI_CH0, baudrate = SPI_FREQ, polarity=0, phase=0, bits=8, sck=Pin(SPI_CLK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
    cs = Pin(SPI_CS, Pin.OUT)
    max31855 = MAX31855(spi, cs)

    #
    # setup LCD
    #
    i2c = I2C(I2C_CH1, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=I2C_FREQ)
    lcd = ST7032LCD(i2c)

    while True:
        tc_temp, int_temp, temp_NIST, status = max31855.get_temperature()
        print('--------------------')
        print(f'Thermocouple Temp: {tc_temp}')
        print(f'Internal Temp: {int_temp}')
        print(f'NIST Temp: {temp_NIST}')
        print(f'status: {status}')

        if status == 'OK':
            msg = f'temp: {tc_temp:0.2f}\n(NIST: {temp_NIST:0.2f})'
        else:
            msg = status
        lcd.print(msg, cls = True)

        time.sleep(1)



main()


#
# end of file
#
