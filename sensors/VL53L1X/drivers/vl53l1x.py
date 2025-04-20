#
# VL53L1X  V0.01 2025/4/20  1st proto type 
#
#
# https://qiita.com/t-a495/items/2e912da660916856e385
# https://github.com/openmv/openmv/blob/master/scripts/libraries/vl53l1x.py
# https://github.com/adafruit/Adafruit_CircuitPython_VL53L1X/blob/ca9a18db70b14353301af435cba397844dbfba73/adafruit_vl53l1x.py
#

from machine import I2C
from machine import Pin
import time

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
  0x01, # 0x86 : clear interrupt, use ClearInterrupt() */
  0x40  # 0x87 : start ranging, use StartRanging() or StopRanging(), If you want an automatic start after VL53L1X_init() call, put 0x40 in location 0x87 */
))


_VL53L1X_I2C_SLAVE_DEVICE_ADDRESS = const(0x0001)
_VL53L1X_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND = const(0x0008)
_GPIO_HV_MUX__CTRL = const(0x0030)
_GPIO__TIO_HV_STATUS = const(0x0031)
_RANGE_CONFIG__TIMEOUT_MACROP_A_HI = const(0x005E)
_RANGE_CONFIG__VCSEL_PERIOD_A = const(0x0060)
_RANGE_CONFIG__TIMEOUT_MACROP_B_HI = const(0x0061)
_RANGE_CONFIG__VCSEL_PERIOD_B = const(0x0063)
_RANGE_CONFIG__VALID_PHASE_HIGH = const(0x0069)
_SD_CONFIG__WOI_SD0 = const(0x0078)
_SD_CONFIG__INITIAL_PHASE_SD0 = const(0x007A)
_ROI_CONFIG__USER_ROI_CENTRE_SPAD = const(0x007F)
_ROI_CONFIG__USER_ROI_REQUESTED_GLOBAL_XY_SIZE = const(0x0080)
_SYSTEM__INTERRUPT_CLEAR = const(0x0086)


_VL53L1X_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0 = const(0x0096)
_VL53L1X_IDENTIFICATION_MODEL_ID = const(0x010F)


REG_RESULT_RANGE_STATUS = 0x0089
REG_PHASECAL_CONFIG_TIMEOUT_MACROP = 0x004B
REG_SYSTEM_MODE_START = 0x0087
REG_IDENTIFICATION_MODEL_ID = 0x010F



#
# reg_addr:  read register address
# size:      read size
# return bytes (size of bytes is specified size)
#
def read_reg(reg_addr, size):
    data = i2c.readfrom_mem(DEVICE_ADDR, reg_addr, size, addrsize=16)
    return data

def write_reg(reg_addr, value):
    i2c.writeto_mem(DEVICE_ADDR, reg_addr, value, addrsize=16)


# >>> read_model_id()
# 60108
# >>> hex(read_model_id())
# '0xeacc'
def read_model_id():
    value = read_reg(REG_IDENTIFICATION_MODEL_ID, 2)  # read 2byte
    return (value[0] << 8) + value[1]
   
#def reset():
#     write_reg(0x0000, bytes(0x00,))
#     time.sleep_ms(100)             # machine.lightsleep(100)
#     write_reg(0x0000, bytes(0x01,))

def __init__():
     #reset()
     time.sleep_ms(1)
     if read_model_id() != 0xEACC:
           raise RuntimeError('Failed to find expected ID register values. Check wiring!')
     write_reg(0x002D, VL51L1X_DEFAULT_CONFIGURATION)
     #write_reg(0x001E, read_reg(0x0022) * 4)  # <<<???
     time.sleep_ms(200)

#
# check distance mode and return setting
# 1:  short distance mode
# 2:  long distance mode
#
def get_distance_mode():
    value = read_reg(REG_PHASECAL_CONFIG_TIMEOUT_MACROP, 1)[0]  # read 1byte
    if value == 0x14:
       return 1        # short distance
    elif value == 0x0A:
       return 2        # long distance
    else:
       None            # unknown setting

def get_distance():
    data = read_reg(REG_RESULT_RANGE_STATUS, 17)
    #range_status = data[0]
    #stream_count = data[2]
    final_crosstalk_corrected_range_mm_sd0 = (data[13] << 8) + data[14]
    return final_crosstalk_corrected_range_mm_sd0 / 10


#__init__()


DEVICE_ADDR = 0x29
i2c = I2C(0)   # default setting :  scl=Pin(5), sda=Pin(4)
__init__()

while True:
  print(f"dist: {get_distance()} cm")
  time.sleep(0.5)

