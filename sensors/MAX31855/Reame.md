# Driver and sample code for MAX31855 and K-type thermocouple probe



python sample code (subscribe sample for )
```
#!/usr/bin/python3

import paho.mqtt.client as mqtt

# 1883 : MQTT, unencrypted, unauthenticated
# URL: https://test.mosquitto.org/
HOST='test.mosquitto.org'
BROKER = 'test.mosquitto.org'
PORT = 1883
TOPIC = "rpi_pico2w/thermopile/"

def on_message(client, userdata, message):
    print(f"{message.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
client.loop_forever()
```
