# 
# Sensor Client
#
# air quality sensor: BME280 connect with I2C
# IoT Platform:  ThingsBoard connect with MQTT
#

# required BME280 driver 
# by Robert Hammelrath
# https://github.com/robert-hh/BME280
# file:  https://github.com/robert-hh/BME280/blob/master/bme280_float.py
#

import time
import json
from umqtt.simple import MQTTClient

from bme280_float import BME280
from machine import I2C


MQTT_BROKER = "192.168.10.100"  # ThingsBoard Server running on Raspberry Pi
MQTT_PORT = 1883
MQTT_TOPIC = "v1/devices/me/telemetry"

CLIENT_ID = 'set_your_client_id'
USER_NAME = 'set_your_user_name'
PASSWORD = 'set_your_password'

def connect():
    print('Connect to ThingsBoard by MQTT')
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT, USER_NAME, PASSWORD)
    client.connect()
    return client

def reconnect():
    print('Failed to connect to ThingsBard, Reconnecting...')
    time.sleep(5)
    client.reconnect()


def setup_sensor(i2c):

    # check connection BME280
    print(i2c.scan()[0])

    # setup BME280
    bme280 = BME280(i2c=i2c)
    return bme280

def main():

    # setup I2C for connect BME280
    i2c = I2C(0, scl=5, sda=4, freq=10_000)
    bme280 = setup_sensor(i2c)

    #connect IoT PF by MQTT
    try:
        client = connect()
    except OSError as e:
        reconnect()

    # report measured data to ThingsBoard by MQTT Publish
    while True:
        for nth in range(100):
            temp, raw_pressure, humidity = bme280.read_compensated_data()
            pressure = raw_pressure / 100
            message  = {'bme280.temp' : temp, 'bme280.pressure' : pressure, 'bme280.humidity' : humidity}
            print(f'send message {message} on topic: {TOPIC}')
            client.publish(TOPIC, json.dumps(message), qos=0)
            time.sleep(30)
