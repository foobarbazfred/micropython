#
# driver for color sensor ; S13683-03DT:
#
#

REG_CTRL=0x00
REG_MANUAL_TIMING = 0x01
REG_RGB_SENSOR = 0x03
RGB_SENSOR_LENGTH = 8

HIGH_GAIN = 0b0000_1000
LOW_GAIN = 0x00
INTEGRATION_TIME_LONG = 0b11        #  11:179.2ms
INTEGRATION_TIME_SL_LONG = 0b10     #  10:22.4ms
INTEGRATION_TIME_SL_SHORT = 0b01    #  01:1.4ms 
INTEGRATION_TIME_SHORT = 0b00       #  00:87.5us

I2C_ADDR=0x2a

class S13683_03DT:

    def __init__(self,i2c):
        self._i2c = i2c    
        self._init_sensor()
        self._setup_sensor()
    
    def _init_sensor(self):
        self.write_control_reg(0xe4)   # RESET,WAIT_MODE,MANUAL_SETTING_MODE
        self.write_manual_timing_reg(0x0c,0x40)   #   Tint 00 , 546ms
    
    def _setup_sensor(self):
        ctrl_params = 0x80 + HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # RESET,High gain
        self.write_control_reg(ctrl_params)  
        ctrl_params = HIGH_GAIN + INTEGRATION_TIME_SL_LONG   # startsensing
        self.write_control_reg(ctrl_params)  
    
    def write_control_reg(self, data):
        bytes_data = bytes((data,))
        self._i2c.writeto_mem(I2C_ADDR, REG_CTRL, bytes_data)
    
    def read_control_reg(self):
        return self._i2c.readfrom_mem(I2C_ADDR, REG_CTRL, 1)[0]
    
    def write_manual_timing_reg(self, upper_byte, lower_byte):
        bytes_data = bytes((upper_byte, lower_byte))
        self._i2c.writeto_mem(I2C_ADDR, REG_MANUAL_TIMING, bytes_data)
    
    def read_rgb_regs(self):
        data = self._i2c.readfrom_mem(I2C_ADDR, REG_RGB_SENSOR, RGB_SENSOR_LENGTH)
        r = (data[0] << 8) + data[1]
        g = (data[2] << 8) + data[3]
        b = (data[4] << 8) + data[5]
        adjust = (data[6] << 8) + data[7]
        return (r, g, b, adjust)
    
    
