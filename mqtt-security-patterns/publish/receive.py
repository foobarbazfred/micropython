#!/usr/bin/python3

# Receive Sample source
# for Python3 with paho.mqtt.client
#

import paho.mqtt.client as mqtt

MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected with reason code", reason_code)
    client.subscribe("test/upy_publish_test", qos=0)

# message callback
def on_message(client, userdata, message):
    print('------------------------')
    print('Topic:', message.topic)
    print('userdata:', userdata)
    print('Payload:', message.payload)
    print('QoS:', message.qos)

# create MQTT Client
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT)

# check message
client.loop_forever()
