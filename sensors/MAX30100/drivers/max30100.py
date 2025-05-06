#
# read write functions for MAX30100 Regisers
#

#
# register address
#
REG_INTR_STAT = 0x00
REG_INTR_ENB = 0x01

REG_FIFO_WR_PTR = 0x02
REG_FIFO_OVF_CNTR = 0x03
REG_FIFO_RD_PTR = 0x04
REG_FIFO_DATA = 0x05
REG_MODE_CONF = 0x06
REG_SPO2_CONF = 0x07
REG_LED_CONF = 0x09
REG_TEMP_INT = 0x16
REG_TEMP_FRAC = 0x17
REG_REV_ID = 0xFE
REG_PART_ID = 0xFF

DEV_ADDR = 0x57

FIFO_SIZE = 16
FIFO_DEPTH = 16

import time

class MAX30100:

    def __init__(self, i2c, dev_addr = DEV_ADDR):   # , dev_addr = DEV_ADDR): work-around
        self._dev_addr = dev_addr
        self._i2c = i2c

    def setup(self):
    
       # reset
       print('reset device')
       CONF_RESET = 0b0100_0000
       self.write_mode_configuration(CONF_RESET)
       time.sleep(0.1)
    
       #
       # wait until PWR_RDY
       #
       while False:
       #while True:
           data = self.read_interrupt_status()
           if data & 0b0000_0001:  # PWR_RDY
               print('PWR_RDY OK')
               break
           else:
               time.sleep(0.1)
    
       #
       print('intrrupt enable')
       data = 0b11110000
       self.write_interrupt_enable(data)
    
       # temprature enable
       print('temp enable')
       CONF_TEMP_EN = 0b0000_1000
       self.write_mode_configuration(CONF_TEMP_EN)
    
       #
       # wait until TEMP_RDY
       #
       while True:
           data = self.read_interrupt_status()
           if data & 0b0100_0000:  # TEMP_RDY
               print('TEMP_RDY OK')
               break
           else:
               time.sleep(0.1)
    
       # get temperature
       print(self.read_temperature())
    
       # set LED Pulse width   0b11 (pulse width:1600, 16bit)
       config = 0b0000_0011       # LED_PW:0b11
       self.write_SPO2_configuration(config)
    
       # https://github.com/devxplained/MAX3010x-Sensor-Library/blob/main/src/MAX30100.cpp
       # LED:14.2  IR:20.8
       # set LED config
       config = 0b0100_0110       # LED_current control
       self.write_LED_configuration(config)
    
       # reset FIFO
       print('reset FIFO pointers')
       self.write_FIFO_read_pointer(0)
       self.write_FIFO_write_pointer(0)
       self.write_FIFO_overflow_counter(0)
    
       # MODE Control: HR enabled
       print('HR enable')
       CONF_MODE_HR_ONLY_ENABLE = 0b0000_0010   # 010 : H2 Enable
       self.write_mode_configuration(CONF_MODE_HR_ONLY_ENABLE)
    
       while True:
           data = self.read_interrupt_status()
           if data & 0b0010_0000:  # HR_RDY
               print('HR_RDY OK')
               break
           else:
               time.sleep(0.1)
    
       return True

    def clear_ovfl_data(self):
       samples = []
       for _ in range(FIFO_DEPTH):
            intr = self.read_interrupt_status()
            rx = self.read_FIFO_read_pointer()
            wx = self.read_FIFO_write_pointer()
            ovfl = self.read_FIFO_overflow_counter()
            prev_status = (intr,rx,wx,ovfl)
            data0 = self.read_FIFO_data()
            data1 = self.read_FIFO_data()
            data2 = self.read_FIFO_data()
            data3 = self.read_FIFO_data()
            intr = self.read_interrupt_status()
            rx = self.read_FIFO_read_pointer()
            wx = self.read_FIFO_write_pointer()
            ovfl = self.read_FIFO_overflow_counter()
            aft_status = (intr,rx,wx,ovfl)
            samples.append((prev_status,(data0,data1,data2,data3),aft_status))
       return samples
    
    

    def get_n_of_samples_in_FIFO(self):
       rd_ptr = self.read_FIFO_read_pointer()
       wr_ptr = self.read_FIFO_write_pointer()
       n_of_samples = wr_ptr - rd_ptr
       if n_of_samples < 0:
           n_of_samples += FIFO_SIZE
       return n_of_samples
    
    def read_temperature(self):
        temp = self.read_temp_int()
        temp += self.read_temp_frac()  / 16.0   # 0.0625 (1/16)
        return temp

    def read_interrupt_status(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_INTR_STAT, 1)[0]
    
    def read_interrupt_enable(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_INTR_ENB, 1)[0]
    
    def write_interrupt_enable(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_INTR_ENB, write_data)
    
    def read_FIFO_read_pointer(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_FIFO_RD_PTR, 1)[0]
    
    def write_FIFO_read_pointer(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_FIFO_RD_PTR, write_data)
    
    def read_FIFO_write_pointer(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_FIFO_WR_PTR, 1)[0]
    
    def write_FIFO_write_pointer(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_FIFO_WR_PTR, write_data)
    
    def read_FIFO_overflow_counter(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_FIFO_OVF_CNTR, 1)[0]
    
    def write_FIFO_overflow_counter(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_FIFO_OVF_CNTR, write_data)
    
    def read_FIFO_data(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_FIFO_DATA, 1)[0]

    def read_FIFO_data_4B(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_FIFO_DATA, 4)
    
    def read_mode_configuration(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_MODE_CONF, 1)[0]
    
    def write_mode_configuration(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_MODE_CONF, write_data)
    
    def read_SPO2_configuration(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_SPO2_CONF, 1)[0]
    
    def write_SPO2_configuration(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_SPO2_CONF, write_data)
    
    def read_LED_configuration(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_LED_CONF, 1)[0]
    
    def write_LED_configuration(self, data):
        write_data = bytes((data,))
        self._i2c.writeto_mem(self._dev_addr, REG_LED_CONF, write_data)
    
    def read_temp_int(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_TEMP_INT, 1)[0]
    
    def read_temp_frac(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_TEMP_FRAC, 1)[0]
    
    def read_rev_id(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_REV_ID, 1)[0]
    
    def read_part_id(self):
        return self._i2c.readfrom_mem(self._dev_addr, REG_PART_ID, 1)[0]
    
    def dump_registers(self):
        for addr in range(0xA):
            data = self._i2c.readfrom_mem(self._dev_addr,addr,1)[0]
            print(f'{addr:02x}: {data:02x}({data:08b})')
    
    
