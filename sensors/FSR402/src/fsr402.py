#
#  FSR402 Driver
#


from machine import ADC
import time

PIN_ADC0=26

SAMPLIG_SIZE=21
value_list = [0] * SAMPLIG_SIZE


# Resistance value of the resistor connected to the sensor, 
# serially connected to GND
VALUE_OF_REGISTER_1 = 991   # The unit is ohms

# Voltage of VCC
VCC_VOLTAGE = 3.3

adc = ADC(PIN_ADC0)        # 

def median_filter(value_list):
    calc_buf  = value_list.copy()
    calc_buf.sort()
    center_value = calc_buf[int(len(calc_buf)/2)]
    return center_value


#
# estimating weight from resistance value
#
def estimate_weight(resistance):
    # Conversion formula for estimating weight from resistance value
    weight = 3.33 * (1 / (resistance/1000.0) - 0.2)
    return weight


def measure():
    while True:
        for _ in range(25):
            adc_val = adc.read_u16()  # 
            value_list.append(adc_val)
            _ = value_list.pop(0)     # to avoid print out
            time.sleep(0.02)
    
        filterd_val = median_filter(value_list)
        vol = 3.3 * filterd_val / 65535   # 0v - 2V
        if vol != 0:
            resistance = VALUE_OF_REGISTER_1 * (VCC_VOLTAGE - vol) / vol
            weight = estimate_weight(resistance)
        else:
            register = 0
            weight = 0
        print(f'{weight}(Kg)')
        print(f'{register/1000} (K Ohm), {vol}V, {filterd_val}')
    
#
#
#
measure()



#
#
#
