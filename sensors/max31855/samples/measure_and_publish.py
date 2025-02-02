import time
import ntptime
import json
from machine import Pin, SPI
from umqtt.simple import MQTTClient

from max31855 import MAX31855

#
# defs for ThingsBoard MQTT Connection
#
SERVER="192.168.10.100"
USERID="X5g3fQ6o1VCAqcNVYKBj"
CLIENT_ID="RPi_1234"
MQTT_TOPIC = 'v1/devices/me/telemetry'


#
# defs for MAX31855
#
SPI_CH = 0  # SPI0
GP_CLK = 2  # SPI0_CLK : Pin 2
GP_MOSI = 3 # SPI0_MOSI : Pin 3
GP_MISO = 4 # SPI0_MISO : Pin 4
GP_CS = 5   # SPI CS : Pin 2
SPI_CLK = 5_000_000  # SPI Clock 50KHz



#
# setup MQTT
#
ntptime.settime()
client = MQTTClient(CLIENT_ID, SERVER, 1883, USERID, '')
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
    (tc_temp, int_temp, status) = max31855.get_temperature()
    msg = json.dumps({'temperature' : tc_temp})
    print('publish:', msg)
    client.publish(MQTT_TOPIC, msg)
    time.sleep(10)

