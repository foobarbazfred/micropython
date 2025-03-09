#
#  FSR402 Driver
#
#  0.01 (2025/3/9 17:00)
#     estimate weight by  quadratic equation
#  0.02 (2025/3/9 17:00)
#     refactor source code
# 

from machine import ADC
import time

PIN_ADC0 = 26

SAMPLIG_SIZE = 21
samplig_data_list = [0] * SAMPLIG_SIZE

# Resistance value of the resistor connected to the sensor, 
# serially connected to GND
VALUE_OF_REGISTER_1 = 991   # The unit is ohms

WEIGHT_OF_STAND = 0.2  # 200g

# Voltage of VCC
VCC_VOLTAGE = 3.3

adc = ADC(PIN_ADC0)         

def median_filter(samplig_data_list):
    calc_buf  = samplig_data_list.copy()
    calc_buf.sort()
    center_value = calc_buf[int(len(calc_buf)/2)]
    return center_value


#
# estimating weight from resistance value
#
# w = 2.4/(R*R) + 0.5
# w: weight (Kg)
# r: registance value (K Ohm)
#
def estimate_weight(resistance):
    if resistance == 0:
       return 0
    # Conversion formula for estimating weight from resistance value
    weight = 2.4  / ((resistance/1000.0)  * (resistance/1000.0) ) + 0.5
    return weight

def estimate_weight_linear(resistance):
    if resistence == 0:
       return 0
    # Conversion formula for estimating weight from resistance value
    weight = 3.33 * (1 / (resistance/1000.0) - 0.2)
    return weight


def measure_weight():
    register = 0
    weight = 0
    while True:
        #
        # sampling ADC data (25 times)
        #
        for _ in range(25):
            adc_val = adc.read_u16()  # 
            samplig_data_list.append(adc_val)
            _ = samplig_data_list.pop(0)     # to avoid print out
            time.sleep(0.02)
    
        #
        # get filterd data (median filter)
        #
        filterd_val = median_filter(samplig_data_list)
        # 
        # convert ADC value to voltage
        # 
        vol = 3.3 * filterd_val / 65535   # 0v - 2V
        if vol != 0:
            #
            # calcurate regsitance value of sensor
            #
            resistance = VALUE_OF_REGISTER_1 * (VCC_VOLTAGE - vol) / vol
            if resistance != 0:
                #
                # estimate weight from resistance with formula
                #
                weight = estimate_weight(resistance) - WEIGHT_OF_STAND
            else:
                weight = 0
        else:
            resistance = 0
            weight = 0
        if weight < 0 :
              weight = '***'
              print(f'{weight}(Kg)')
        else:
              print(f'{weight}(Kg)')
        print(f'{resistance/1000} (K Ohm), {vol}V, {filterd_val}')
    
#
#
#
measure_weight()



#
#
#
