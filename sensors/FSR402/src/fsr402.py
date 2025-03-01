#
#  FST402 Driver
#


from machine import ADC
import time

PIN_ADC0=26


adc = ADC(PIN_ADC0)        # 



while True:
    val = adc.read_u16()  # 
    vol = 3.3 * val / 65535   # 0v - 2V
    if vol != 0:
        sr = 991 * (3.3 - vol) / vol
    else:
        sr = 0
    print(f'{sr/1000} (Kohm), {vol}V, {val}')
    time.sleep(0.5)


#
#
#