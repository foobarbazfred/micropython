import time
import ntptime
import json
from machine import Pin, SPI
from umqtt.simple import MQTTClient

from max31855 import MAX31855

#
# K-type thermocouple parts id
#
PART_ID1 = 'NR-39Y-Y'        # https://akizukidenshi.com/catalog/g/g117400/
PART_ID2 = 'NR-39B'          # https://akizukidenshi.com/catalog/g/g110750/

#
# defs for misquitto broker connection
#
SERVER = "test.mosquitto.org"
PORT = 1883
CLIENT_ID="RPi_1234"
MQTT_TOPIC = 'rpi_pico2w/thermopile/'

#
# defs for MAX31855
#
SPI_CH = 0  # SPI0
GP_CLK = 2  # SPI0_CLK  : GP2 [4]
GP_MOSI = 3 # SPI0_MOSI : GP3 [5]
GP_MISO = 4 # SPI0_MISO : GP4 [6]
GP_CS = 5   # SPI CS    : GP5 [7]
SPI_CLK = 5_000_000  # SPI Clock 500KHz



#
# setup MQTT
#
ntptime.settime()
client = MQTTClient(CLIENT_ID, SERVER, PORT)
client.connect()

#
# setup  Thermocomple Temperature Sensor
#
spi = SPI(SPI_CH, baudrate=SPI_CLK, polarity=0, phase=0, bits=8, sck=Pin(GP_CLK), mosi=Pin(GP_MOSI), miso=Pin(GP_MISO))
cs = Pin(GP_CS, Pin.OUT)
#
# initialize MAX31855
#
max31855 = MAX31855(spi, cs)


#
# measure temprature and publish
#
while True:
    tc_temp, int_temp, temp_NIST, status = max31855.get_temperature()
    if status == 'OK':
        msg = json.dumps({'temperature' : tc_temp, 'part_id' : PART_ID1})
        (yy, mm, dd, hh, mm, ss, x, y ) = time.localtime()
        print('publish:', msg, f"at {hh+9}:{mm}:{ss}")
        client.publish(MQTT_TOPIC, msg)
    time.sleep(10)
