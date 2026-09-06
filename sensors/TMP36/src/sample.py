#
# sample for TMP36
#
import time
from machine import ADC, Pin

SENSER_PIN=26
temp_sensor = ADC(Pin(SENSER_PIN))

VERBOSE=False

CONST_A = 107.14285714285715
CONST_B = -57.14285714285717

def conv_volt_to_temp(volt):
    return CONST_A * volt  + CONST_B

while True:
    volt = 3.3 * temp_sensor.read_u16() / 65535
    if VERBOSE:
        print(volt,'V')
        print(conv_volt_to_temp(volt),'C')
    else:
        print(conv_volt_to_temp(volt))
    time.sleep(1)


