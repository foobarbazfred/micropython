# sample 02
# with TLS and no auth
#
from umqtt.simple import MQTTClient
import json

MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 8883
MQTT_TOPIC = b'test/upy_publish_test'
MQTT_CLIENT_ID = "client_RP_Pico2W_0001"

client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, ssl=True)
client.connect()
message = {'client_id': MQTT_CLIENT_ID , 'security settings' : 'with TLS and no Auth'}
payload = json.dumps(message).encode('utf-8')
print("publish:", payload)
client.publish(MQTT_TOPIC, payload)
client.disconnect()
