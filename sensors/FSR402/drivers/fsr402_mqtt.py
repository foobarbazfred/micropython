# pub.py
import time
from umqtt.simple import MQTTClient

MQTT_BROKER = "192.168.10.100"
CLIENT_ID = 'RPi-pico-001'
USER_ID = "pico000"
PASSWD = "zzz"
PORT = 1883
TOPIC = "rpi-pico-001/sensor"
MSG = '{"data" : 123}'

def connect():
    print('Connected to MQTT Broker')
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, PORT, USER_ID, PASSWD)
    client.connect()
    return client

def reconnect():
    print('Failed to connect to MQTT broker, Reconnecting...')
    time.sleep(5)
    client.reconnect()

try:
    client = connect()
except OSError as e:
    reconnect()


#
#  FST402 Driver
#


from machine import ADC
import time

PIN_ADC0=26


adc = ADC(PIN_ADC0)        # 





import random
import json
import math
import time

def get_datetime():
   (year,month,day,hour,min,sec,_,_) = time.localtime()
   return f'{year}/{month}/{day} {hour+9}:{min}:{sec}'

def get_regist():
    val = adc.read_u16()  # 
    vol = 3.3 * val / 65535   # 0v - 2V
    if vol != 0:
        sr = 991 * (3.3 - vol) / vol
    else:
        sr = 0
    return sr/1000

def main():
  while True:
    for nth in range(100):
      value = 100 * math.sin(2 * math.pi * nth / 100)
      msg = {"regist" : get_regist(), 'datetime' : get_datetime()}
      print(f'send message {msg} on topic: {TOPIC}')
      client.publish(TOPIC, json.dumps(msg), qos=0)
      time.sleep_ms(10)


main()

