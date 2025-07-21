#
# sample05.py
#
from umqtt.simple import MQTTClient
import ssl
import json

MQTT_BROKER = 'test.mosquitto.org'
#MQTT_PORT = 8885     # 8885 : MQTT, encrypted, authenticated
MQTT_PORT = 8887     # 8887 : MQTT, encrypted, authenticated, server certificate deliberately expired
MQTT_TOPIC = b'test/upy_publish_test'
MQTT_CLIENT_ID = "client_RP_Pico2W_0001"
MQTT_USER = 'ro'
MQTT_PASSWORD ='readonly' 
SERVER_CRT_FILE = 'mosquitto.org.crt.der'

# read Server side ROOT CA (DER format)
with open(SERVER_CRT_FILE, "rb") as f:
     cadata = f.read()

# parameters for mTLS
ssl_params = {
    'cadata' : cadata,
    "cert_reqs" : ssl.CERT_REQUIRED,
    'server_hostname' : MQTT_BROKER,
}
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT,
                     user = MQTT_USER, password = MQTT_PASSWORD,
                     ssl = True,  ssl_params = ssl_params )
client.connect()
message = {'client_id': MQTT_CLIENT_ID , 'security settings' : 'with TLS and Auth by ID/PWD'}
payload = json.dumps(message).encode('utf-8')
client.publish(MQTT_TOPIC, payload)
client.disconnect()
