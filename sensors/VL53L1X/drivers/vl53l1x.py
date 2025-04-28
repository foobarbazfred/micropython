#
# driver for VL53L1X 
#   V0.01 2025/4/20  1st proto type 
#   V0.02 2025/4/26  2nd proto
#   V0.03 2025/4/26  refactor to class
#   V0.04 2025/4/26  bug fix  _get_interrupt_polarity()
#   V0.05 2025/4/26  refactor:  change class name 
#   V0.06 2025/4/26  refactor:  
#   V0.06 2025/4/26  refactor:  add function , wait_data_ready()
#
# List of referenced sources used in the development of this code
#   https://github.com/adafruit/Adafruit_CircuitPython_VL53L1X/blob/ca9a18db70b14353301af435cba397844dbfba73/adafruit_vl53l1x.py
#   https://github.com/openmv/openmv/blob/master/scripts/libraries/vl53l1x.py
#   https://github.com/rneurink/VL53L1X_ULD/blob/master/src/core/VL53L1X_api.cpp
#   https://github.com/embvm-drivers/ST-VL53L1X/blob/main/src/vl53l1x.cpp
#   https://qiita.com/t-a495/items/2e912da660916856e385
#

import time

#
# note: Reusing VL51L1X configuration parameters
#
VL51L1X_DEFAULT_CONFIGURATION = bytes((
  0x00, # 0x2d : set bit 2 and 5 to 1 for fast plus mode (1MHz I2C), else don't touch */
  0x00, # 0x2e : bit 0 if I2C pulled up at 1.8V, else set bit 0 to 1 (pull up at AVDD) */
  0x00, # 0x2f : bit 0 if GPIO pulled up at 1.8V, else set bit 0 to 1 (pull up at AVDD) */
  0x01, # 0x30 : set bit 4 to 0 for active high interrupt and 1 for active low (bits 3:0 must be 0x1), use SetInterruptPolarity() */
  0x02, # 0x31 : bit 1 = interrupt depending on the polarity, use CheckForDataReady() */
  0x00, # 0x32 : not user-modifiable */
  0x02, # 0x33 : not user-modifiable */
  0x08, # 0x34 : not user-modifiable */
  0x00, # 0x35 : not user-modifiable */
  0x08, # 0x36 : not user-modifiable */
  0x10, # 0x37 : not user-modifiable */
  0x01, # 0x38 : not user-modifiable */
  0x01, # 0x39 : not user-modifiable */
  0x00, # 0x3a : not user-modifiable */
  0x00, # 0x3b : not user-modifiable */
  0x00, # 0x3c : not user-modifiable */
  0x00, # 0x3d : not user-modifiable */
  0xff, # 0x3e : not user-modifiable */
  0x00, # 0x3f : not user-modifiable */
  0x0F, # 0x40 : not user-modifiable */
  0x00, # 0x41 : not user-modifiable */
  0x00, # 0x42 : not user-modifiable */
  0x00, # 0x43 : not user-modifiable */
  0x00, # 0x44 : not user-modifiable */
  0x00, # 0x45 : not user-modifiable */
  0x20, # 0x46 : interrupt configuration 0->level low detection, 1-> level high, 2-> Out of window, 3->In window, 0x20-> New sample ready , TBC */
  0x0b, # 0x47 : not user-modifiable */
  0x00, # 0x48 : not user-modifiable */
  0x00, # 0x49 : not user-modifiable */
  0x02, # 0x4a : not user-modifiable */
  0x0a, # 0x4b : not user-modifiable */
  0x21, # 0x4c : not user-modifiable */
  0x00, # 0x4d : not user-modifiable */
  0x00, # 0x4e : not user-modifiable */
  0x05, # 0x4f : not user-modifiable */
  0x00, # 0x50 : not user-modifiable */
  0x00, # 0x51 : not user-modifiable */
  0x00, # 0x52 : not user-modifiable */
  0x00, # 0x53 : not user-modifiable */
  0xc8, # 0x54 : not user-modifiable */
  0x00, # 0x55 : not user-modifiable */
  0x00, # 0x56 : not user-modifiable */
  0x38, # 0x57 : not user-modifiable */
  0xff, # 0x58 : not user-modifiable */
  0x01, # 0x59 : not user-modifiable */
  0x00, # 0x5a : not user-modifiable */
  0x08, # 0x5b : not user-modifiable */
  0x00, # 0x5c : not user-modifiable */
  0x00, # 0x5d : not user-modifiable */
  0x01, # 0x5e : not user-modifiable */
  0xdb, # 0x5f : not user-modifiable */
  0x0f, # 0x60 : not user-modifiable */
  0x01, # 0x61 : not user-modifiable */
  0xf1, # 0x62 : not user-modifiable */
  0x0d, # 0x63 : not user-modifiable */
  0x01, # 0x64 : Sigma threshold MSB (mm in 14.2 format for MSB+LSB), use SetSigmaThreshold(), default value 90 mm  */
  0x68, # 0x65 : Sigma threshold LSB */
  0x00, # 0x66 : Min count Rate MSB (MCPS in 9.7 format for MSB+LSB), use SetSignalThreshold() */
  0x80, # 0x67 : Min count Rate LSB */
  0x08, # 0x68 : not user-modifiable */
  0xb8, # 0x69 : not user-modifiable */
  0x00, # 0x6a : not user-modifiable */
  0x00, # 0x6b : not user-modifiable */
  0x00, # 0x6c : Intermeasurement period MSB, 32 bits register, use SetIntermeasurementInMs() */
  0x00, # 0x6d : Intermeasurement period */
  0x0f, # 0x6e : Intermeasurement period */
  0x89, # 0x6f : Intermeasurement period LSB */
  0x00, # 0x70 : not user-modifiable */
  0x00, # 0x71 : not user-modifiable */
  0x00, # 0x72 : distance threshold high MSB (in mm, MSB+LSB), use SetD:tanceThreshold() */
  0x00, # 0x73 : distance threshold high LSB */
  0x00, # 0x74 : distance threshold low MSB ( in mm, MSB+LSB), use SetD:tanceThreshold() */
  0x00, # 0x75 : distance threshold low LSB */
  0x00, # 0x76 : not user-modifiable */
  0x01, # 0x77 : not user-modifiable */
  0x0f, # 0x78 : not user-modifiable */
  0x0d, # 0x79 : not user-modifiable */
  0x0e, # 0x7a : not user-modifiable */
  0x0e, # 0x7b : not user-modifiable */
  0x00, # 0x7c : not user-modifiable */
  0x00, # 0x7d : not user-modifiable */
  0x02, # 0x7e : not user-modifiable */
  0xc7, # 0x7f : ROI center, use SetROI() */
  0xff, # 0x80 : XY ROI (X=Width, Y=Height), use SetROI() */
  0x9B, # 0x81 : not user-modifiable */
  0x00, # 0x82 : not user-modifiable */
  0x00, # 0x83 : not user-modifiable */
  0x00, # 0x84 : not user-modifiable */
  0x01, # 0x85 : not user-modifiable */
  0x01, # 0x86 : clear interrupt, 0x01=clear 
  0x00  # 0x87 : ranging  0x00=stop, 0x40=start
))

#
# Definition of timing budget parameters
#

TB_SHORT_DIST = {
    # ms: (MACROP_A_HI, MACROP_B_HI)
    15: ((0x00, 0x1D), (0x00, 0x27)),
    20: ((0x00, 0x51), (0x00, 0x6E)),
    33: ((0x00, 0xD6), (0x00, 0x6E)),
    50: ((0x01, 0xAE), (0x01, 0xE8)),
    100: ((0x02, 0xE1), (0x03, 0x88)),
    200: ((0x03, 0xE1), (0x04, 0x96)),
    500: ((0x05, 0x91), (0x05, 0xC1)),
}

TB_LONG_DIST = {
    # ms: (MACROP_A_HI, MACROP_B_HI)
    20: ((0x00, 0x1E), (0x00, 0x22)),
    33: ((0x00, 0x60), (0x00, 0x6E)),
    50: ((0x00, 0xAD), (0x00, 0xC6)),
    100: ((0x01, 0xCC), (0x01, 0xEA)),
    200: ((0x02, 0xD9), (0x02, 0xF8)),
    500: ((0x04, 0x8F), (0x04, 0xA4)),
}


#
# Definition of register addresses
#
REG_PAD_I2C_HV_CONFIG =   0x002D
REG_GPIO_HV_MUX_CTRL = 0x0030
REG_GPIO_TIO_HV_STATUS = 0x0031
REG_PHASECAL_CONFIG_TIMEOUT_MACROP = 0x004B
REG_RANGE_CONFIG_TIMEOUT_MACROP_A_HI = 0x005E
REG_RANGE_CONFIG_VCSEL_PERIOD_A = 0x0060
REG_RANGE_CONFIG_TIMEOUT_MACROP_B_HI = 0x0061
REG_RANGE_CONFIG_VCSEL_PERIOD_B = 0x0063
REG_RANGE_CONFIG_VALID_PHASE_HIGH = 0x0069
REG_SD_CONFIG_WOI_SD0 = 0x0078
REG_SD_CONFIG_INITIAL_PHASE_SD0 = 0x007A
REG_SYSTEM_INTERRUPT_CLEAR = 0x0086
REG_SYSTEM_MODE_START = 0x0087
REG_RESULT_RANGE_STATUS = 0x0089
REG_RESULT_FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0 = 0x0096
REG_IDENTIFICATION_MODEL_ID = 0x010F


VL53L1X_DEVICE_ADDR = 0x29
RETRY_TIME_OUT = 3000   # retry time out (3sec)

class VL53L1X:

    def __init__(self, i2c, device_addr = VL53L1X_DEVICE_ADDR): 
        self._current_timing_budget = 50   # 50msec
        self._device_addr = device_addr
        self._i2c = i2c

        # check connection
        if len(self._i2c.scan()) > 0 and i2c.scan()[0] == self._device_addr:
            print('device connection is ok')
        else:
            print('Error, can not find device')
            return False # must be changed to raise exception
    
        # check model type
        model_id, model_type, mask_rev = self.get_model_info()
        if model_id != 0xEA or model_type != 0xCC:
            print(f'model ID or model type is not correct')
            print(f'ID:0x{model_id:02X}, type:0x{model_type:02X} req:(0xEA 0xCC)')
            print(f'check device')
            return False   # must be changed to raise exception

        self._device_setup()

    def start_measurement(self):
        self._write_reg(REG_SYSTEM_MODE_START, bytes((0x40,)))
    
    def stop_measurement(self):
        self._write_reg(REG_SYSTEM_MODE_START, bytes((0x00,)))
    
    #
    # read registers and returns distance (cm)
    # Usage notes:
    #    check data is ready before calling this function
    #    e.g.  get_data_ready()  or wait_data_ready()
    #
    def get_distance(self):
        value = self._read_reg(REG_RESULT_FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0, 2)
        distance = ((value[0] << 8) + value[1]) / 10
        return distance
    
    def clear_interrupt(self):
        self._write_reg(REG_SYSTEM_INTERRUPT_CLEAR, bytes((0x01,)))
    
    #
    # check data is ready or not 
    # (not wait until data is ready)
    #
    # return value
    #   True  ... measured data is ready
    #   False ... measured data is not ready
    def get_data_ready(self):
        val = self._read_reg(REG_GPIO_TIO_HV_STATUS, 1)[0]
        if (val & 0x01) == self._get_interrupt_polarity():
            return True
        else:
            return False
    
    #
    # wait until data is ready
    # return value
    #   True  ... measured data is ready
    #   False ... measured data is not ready in retry time
    #
    def wait_data_ready(self, timeout=RETRY_TIME_OUT):
        retry_count = int(timeout / self._current_timing_budget)
        for _ in range(retry_count):
            if self.get_data_ready():
               return True
            else:
               time.wait_ms(self._current_timing_budget)
        return False

    #
    # check distance mode and return setting
    # return value
    #   'short':  short distance mode
    #   'long':  long distance mode
    #
    def get_distance_mode(self):
        value = self._read_reg(REG_PHASECAL_CONFIG_TIMEOUT_MACROP, 1)[0]  # read 1byte
        if value == 0x14:
            return 'short'        # short distance
        elif value == 0x0A:
            return 'long'         # long distance
        else:
            print('internal error in get_distance')
            return False          # unknown setting
    
    # 
    # set distance mode
    # argument:
    #   'long' :  set long distance mode
    #   'short':  set short distance mode
    #
    def set_distance_mode(self, distance_mode):
    
        if distance_mode == 'long':
            self._write_reg(REG_PHASECAL_CONFIG_TIMEOUT_MACROP, bytes((0x0A,)))
            self._write_reg(REG_RANGE_CONFIG_VCSEL_PERIOD_A, bytes((0x0F,)))
            self._write_reg(REG_RANGE_CONFIG_VCSEL_PERIOD_B, bytes((0x0D,)))
            self._write_reg(REG_RANGE_CONFIG_VALID_PHASE_HIGH, bytes((0xB8,)))
            self._write_reg(REG_SD_CONFIG_WOI_SD0, bytes((0x0F, 0x0D)))
            self._write_reg(REG_SD_CONFIG_INITIAL_PHASE_SD0, bytes((0x0E, 0x0E)))
            self._set_timing_budget(distance_mode)
    
        elif distance_mode == 'short':
            self._write_reg(REG_PHASECAL_CONFIG_TIMEOUT_MACROP, bytes((0x14,)))
            self._write_reg(REG_RANGE_CONFIG_VCSEL_PERIOD_A, bytes((0x07,)))
            self._write_reg(REG_RANGE_CONFIG_VCSEL_PERIOD_B, bytes((0x05,)))
            self._write_reg(REG_RANGE_CONFIG_VALID_PHASE_HIGH, bytes((0x38,)))
            self._write_reg(REG_SD_CONFIG_WOI_SD0, bytes((0x07, 0x05)))
            self._write_reg(REG_SD_CONFIG_INITIAL_PHASE_SD0, bytes((0x06, 0x06)))
            self._set_timing_budget(distance_mode)
    
        else:
            print(f'Error: Invalid distance_mode: {distance_mode}')
            return False
    

    #
    # get model info
    # return value
    #   tuple of  ModelID, Model Type, MaskRev
    # '0xea' '0xcc' '0x10'
    #
    def get_model_info(self):
        value = self._read_reg(REG_IDENTIFICATION_MODEL_ID, 3)  # read 3bytes
        return value[0], value[1], value[2]
    

    #------------------------------------------
    #  private functions
    #------------------------------------------

    #
    # setup VL53L1X 
    #
    def _device_setup(self):
        # model type is ok, then setup
        self._write_reg(REG_PAD_I2C_HV_CONFIG, VL51L1X_DEFAULT_CONFIGURATION)
        time.sleep_ms(200)
        self.set_distance_mode('long')

    #
    # returns interrupt polarity
    #
    def _get_interrupt_polarity(self):
        val = self._read_reg(REG_GPIO_HV_MUX_CTRL, 1)[0]
        if (val & 0x10) == 0:
            return 1
        else:
            return 0
    
    #
    # set timing_budget according to distance mode and timing budget
    #
    def _set_timing_budget(self, distance_mode, new_timing = None):

        if new_timing:
            timing = new_timing
        else:
            timing = self._current_timing_budget
    
        if distance_mode == 'short':
            reg_vals = TB_SHORT_DIST
        elif distance_mode == 'long':
            reg_vals = TB_LONG_DIST
        else:
            print("Unknown distance mode.")
            return False
    
        if timing not in reg_vals:
            print("Invalid timing budget.")
            return False
    
        self._write_reg(REG_RANGE_CONFIG_TIMEOUT_MACROP_A_HI, bytes((reg_vals[timing][0])))
        self._write_reg(REG_RANGE_CONFIG_TIMEOUT_MACROP_B_HI, bytes((reg_vals[timing][1])))

        if new_timing:
            self._current_timing_budget = new_timing
    
        return True
    
    #
    # reg_addr:  read register address
    # size:      read size
    # return: bytes (size of bytes is specified size)
    #
    def _read_reg(self, reg_addr, size):
        data = self._i2c.readfrom_mem(self._device_addr, reg_addr, size, addrsize=16)
        return data
    
    #
    # reg_addr:  read register address
    # value:     bytes data
    # return None
    #
    def _write_reg(self, reg_addr, value):
        self._i2c.writeto_mem(self._device_addr, reg_addr, value, addrsize=16)
    

#
# end of file
#
