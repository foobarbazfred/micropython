#
# boot.py sample
#
import network
import ntptime
import time

SSID = 'set_your_wifi_SSD'
PASSWD = 'set_your_wifi_PASSWORD'

def setup_WiFi(id, pwd):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(id, pwd)
    while station.isconnected() == False:
        pass

    print('Connection successful')
    print(station.ifconfig())# Synchronize system time using NTP protocol
    return station

wlan = setup_WiFi(SSID, PASSWD)

# Synchronize system clock using NTP
# Wait briefly to ensure DNS is ready
time.sleep(1)

# Try synchronizing  system clock by  NTP
try:
    ntptime.settime()
    print("Time synchronized:", time.localtime())
except OSError as e:
    print("NTP sync failed:", e)

#
