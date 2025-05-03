#
# Driver for MAX31855
#
# v0.01 2025/3/9 1st version
# v0.02 2025/5/2 bug fix (8bit convert)
# v0.03 2025/5/2 refactor; convert from bit field to signed float type value
# v0.04 2025/5/2 Add new feature;  temperature_NIST (original: [Adafruit_CircuitPython_MAX31855])
# v0.05 2025/5/3 refactor; convert from bit field to signed float type value
# v0.06 2025/5/3 Formatted the source code
#

import uctypes
import struct
import math

#
# Bit-field definition in MAX31855 register
#
REGISTER_BIT_FIELDS = {
   'tc_temp'   : 18 << uctypes.BF_POS | 14 << uctypes.BF_LEN | uctypes.BFUINT32,
   'res1'      : 17 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   'fault_bit' : 16 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   'int_temp'  :  4 << uctypes.BF_POS | 12 << uctypes.BF_LEN | uctypes.BFUINT32,
   'res0'      :  3 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   'scv_bit'   :  2 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   'scg_bit'   :  1 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   'oc_bit'    :  0 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
}

class MAX31855:

    def __init__(self, spi, cs, verbose=False):
        self.spi = spi
        self.cs = cs
        self.verb = verbose

    def get_temperature(self):

        tc_temp = 0
        int_temp = 0 
        temp_NIST = 0
        status = None

        self.cs.low()
        register_values = self.spi.read(4)
        self.cs.high()  
        if self.verb:
            print(register_values)

        tc_temp, int_temp, scv_flag, scg_flag, oc_flag = self._parse_data(register_values)

        if scv_flag == 0 and  scg_flag == 0 and oc_flag == 0:
            status = 'OK'
            temp_NIST = self._temperature_NIST(tc_temp, int_temp)
        else:
            status = 'ERROR'
            if scv_flag == 1:
                   status += ',SVC'
            if scg_flag == 1:
                   status += ',SCG'
            if oc_flag == 1:
                   status +=',OC'
        return (tc_temp, int_temp, temp_NIST, status)
    

    #
    # convert 32bit data  ->  couple_temp, inter_temp, scv_flag, scg_flag, oc_flag
    #
    def _parse_data(self, register_values):

        regs = uctypes.struct(uctypes.addressof(register_values), REGISTER_BIT_FIELDS, uctypes.BIG_ENDIAN)

        scv_flag = regs.scv_bit
        scg_flag = regs.scg_bit
        oc_flag = regs.oc_bit
        tc_temp = regs.tc_temp
        int_temp = regs.int_temp

        # check flag
        if scv_flag == 0 and  scg_flag == 0 and oc_flag == 0:
              # if OK, then proceed
              pass
        else:
              # if ERROR then stop convert and return with None
              return (None, None, scv_flag, scg_flag, oc_flag)

        # 14-Bit Thermocouple Temperature Data
        # integer part: 12 bit + floating part :2 bit
        # convert to signed and float type
        if tc_temp & 0b10_0000_0000_0000:  # if minus flag(MSB) is set
             tc_temp = ((1 << 14) - tc_temp ) * ( -1 ) # convert to signed int type
        tc_temp = tc_temp / (2**2)  # convert to float type (1/2**2 means decimal part is 2bit)
        if self.verb:
            print('tc temp:', tc_temp)

        # 12-BIT INTERNAL TEMPERATURE DATA
        # integer part: 8 bit + floating part :4 bit
        # convert to signed and float type
        if int_temp & 0b1000_0000_0000:  # if minus flag(MSB) is set
             int_temp = ((1 << 12) - int_temp ) * (-1)  # convert to signed int type
        int_temp = int_temp /(2**4)       # convert to float type (1/(2**4) means decimal part is 4bit)
        if self.verb:
            print('int temp:', int_temp)

        return (tc_temp, int_temp, scv_flag, scg_flag, oc_flag)

    #
    # compute temperature by NIST table
    # argument
    #    TR : temperature of remote thermocouple junction
    #    TAMB: temperature of device (cold junction)
    # This function is quoted from the repository [Adafruit_CircuitPython_MAX31855]
    # (https://github.com/adafruit/Adafruit_CircuitPython_MAX31855/blob/main/adafruit_max31855.py)
    #
    def _temperature_NIST(self, TR, TAMB):
        '''
        Thermocouple temperature in degrees Celsius, computed using
        raw voltages and NIST approximation for Type K, see:
        https://srdata.nist.gov/its90/download/type_k.tab
        '''
        # thermocouple voltage based on MAX31855's uV/degC for type K (table 1)
        VOUT = 0.041276 * (TR - TAMB)
        # cold junction equivalent thermocouple voltage
        if TAMB >= 0:
            VREF = (
                -0.176004136860e-01
                + 0.389212049750e-01 * TAMB
                + 0.185587700320e-04 * math.pow(TAMB, 2)
                + -0.994575928740e-07 * math.pow(TAMB, 3)
                + 0.318409457190e-09 * math.pow(TAMB, 4)
                + -0.560728448890e-12 * math.pow(TAMB, 5)
                + 0.560750590590e-15 * math.pow(TAMB, 6)
                + -0.320207200030e-18 * math.pow(TAMB, 7)
                + 0.971511471520e-22 * math.pow(TAMB, 8)
                + -0.121047212750e-25 * math.pow(TAMB, 9)
                + 0.1185976
                * math.exp(-0.1183432e-03 * math.pow(TAMB - 0.1269686e03, 2))
            )
        else:
            VREF = (
                0.394501280250e-01 * TAMB
                + 0.236223735980e-04 * math.pow(TAMB, 2)
                + -0.328589067840e-06 * math.pow(TAMB, 3)
                + -0.499048287770e-08 * math.pow(TAMB, 4)
                + -0.675090591730e-10 * math.pow(TAMB, 5)
                + -0.574103274280e-12 * math.pow(TAMB, 6)
                + -0.310888728940e-14 * math.pow(TAMB, 7)
                + -0.104516093650e-16 * math.pow(TAMB, 8)
                + -0.198892668780e-19 * math.pow(TAMB, 9)
                + -0.163226974860e-22 * math.pow(TAMB, 10)
            )

        # total thermoelectric voltage
        VTOTAL = VOUT + VREF
        # determine coefficients
        # https://srdata.nist.gov/its90/type_k/kcoefficients_inverse.html
        if -5.891 <= VTOTAL <= 0:
            DCOEF = (
                0.0000000e00,
                2.5173462e01,
                -1.1662878e00,
                -1.0833638e00,
                -8.9773540e-01,
                -3.7342377e-01,
                -8.6632643e-02,
                -1.0450598e-02,
                -5.1920577e-04,
            )
        elif 0 < VTOTAL <= 20.644:
            DCOEF = (
                0.000000e00,
                2.508355e01,
                7.860106e-02,
                -2.503131e-01,
                8.315270e-02,
                -1.228034e-02,
                9.804036e-04,
                -4.413030e-05,
                1.057734e-06,
                -1.052755e-08,
            )
        elif 20.644 < VTOTAL <= 54.886:
            DCOEF = (
                -1.318058e02,
                4.830222e01,
                -1.646031e00,
                5.464731e-02,
                -9.650715e-04,
                8.802193e-06,
                -3.110810e-08,
            )
        else:
            raise RuntimeError(f'Total thermoelectric voltage out of range:{VTOTAL}')
        # compute temperature
        TEMPERATURE = 0
        for n, c in enumerate(DCOEF):
            TEMPERATURE += c * math.pow(VTOTAL, n)
        return TEMPERATURE

#
# end of file
#
