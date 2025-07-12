#
# sample04.py
#
# MQTT over TLS with mutual authentication (mTLS) sample.
# Connects to test.mosquitto.org using client certificate authentication,
# publishes a test message, then disconnects.
#

from umqtt.simple import MQTTClient
import ssl
import json

MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 8884                    # 8884 : MQTT, encrypted, client certificate required

MQTT_TOPIC = b'test/upy_publish_test'
MQTT_CLIENT_ID = "client_RP_Pico2W_0001"

CLIENT_KEY_FILE = 'client.key.der'
CLIENT_CRT_FILE = 'client.crt.der'
SERVER_CRT_FILE = 'mosquitto.org.crt.der'

# read Server side ROOT CA (DER format)
with open(SERVER_CRT_FILE, "rb") as f:
     cadata = f.read()

# parameters for mTLS
ssl_params = {
    "key" : CLIENT_KEY_FILE,
    "cert" : CLIENT_CRT_FILE,
    'cadata' : cadata,
    "cert_reqs" : ssl.CERT_REQUIRED,
    'server_hostname' : MQTT_BROKER,
}
client = MQTTClient( MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT, ssl = True, ssl_params = ssl_params )
client.connect()
message = {'client_id': MQTT_CLIENT_ID, 'security settings' : 'with TLS and auth by client crt' }
payload = json.dumps(message).encode('utf-8')
print("publish:", payload)
client.publish(MQTT_TOPIC, payload)
client.disconnect()
