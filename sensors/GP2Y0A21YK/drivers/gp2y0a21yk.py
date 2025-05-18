#
# driver for distance senser GP2Y0A21YK0F
#
# v0.02 (2025/2/11)
# v0.03 (2025/4/29)  refactor: class 
# v0.04 (2025/5/1)  refactor: update convert table
#

import time

#
#  measured data for estimating distance
#  data format: voltage(V) ,  1/distance (1/cm)
#
VOLTAGE_INVDISTANCE_TABLE = (
   (3.126, 1/6),(2.889, 1/7),(2.771, 1/8),
   (2.512, 1/9),(2.375, 1/10),(1.995, 1/12),
   (1.921, 1/14),(1.751, 1/16),(1.580, 1/18),
   (1.452, 1/20),(1.314, 1/25),(1.121, 1/30),
   (1.002, 1/35),
)

SENSOR_MEASUREMENT_TIMING = 40  # interval 40msec
SAMPLIG_SIZE=21
SAMPLING_DELAY=300  #  wait for avoid power line noise (pulse width: 124us,  interval: 1ms)

# 65535: max value of ADC ,  3.3 : Power suppoly volt
MAX_VOLT = 3.3        # voltage of power supply
MAX_VALUE = 65535     # max value of u16 (0xffff)
   
MAX_MEASURABLE_VOLTAGE = 3
MIN_MEASURABLE_VOLTAGE = 1.1


class GP2Y0A21YK:

    def __init__(self,adc):
        self._value_list = [0] * SAMPLIG_SIZE
        self._adc = adc

    def median_filter(self):
        calc_buf  = self._value_list.copy()
        calc_buf.sort()
        center_value = calc_buf[int(len(calc_buf)/2)]
        return center_value
    
    #
    #
    #
    def interpolation(self, vol):
    
       if vol > MAX_MEASURABLE_VOLTAGE:
           print(f'measured volume [{vol}] is too high')
           return None
    
       if vol < MIN_MEASURABLE_VOLTAGE:
           print(f'measured volume [{vol}] is too low')
           return None
    
       for i in range(len(VOLTAGE_INVDISTANCE_TABLE)):
           ref_vol_s = VOLTAGE_INVDISTANCE_TABLE[i]
           ref_vol_e = VOLTAGE_INVDISTANCE_TABLE[i+1]
           if vol >= ref_vol_e[0]:
                slope = (ref_vol_e[1] -  ref_vol_s[1])/(ref_vol_e[0] -  ref_vol_s[0])
                inverse_distance = ref_vol_s[1] + slope * (vol - ref_vol_s[0])
                return 1 / inverse_distance

    #
    #
    #
    def measure_distance(self):

        # sampling data for fill value_list
        for _ in range(SAMPLIG_SIZE):
            raw_vol = MAX_VOLT * self._adc.read_u16() / MAX_VALUE 
            self._value_list.append(raw_vol)
            _ = self._value_list.pop(0)     # to avoid print out
            time.sleep_us(SAMPLING_DELAY)  # wait for avoid power line noise (interval 1ms)
            time.sleep_ms(SENSOR_MEASUREMENT_TIMING)  # wait until sensor output is updated
    
        filterd_value = self.median_filter()
        estim_dist = self.interpolation(filterd_value)
        return estim_dist, filterd_value


    
