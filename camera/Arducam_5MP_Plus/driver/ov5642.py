#
# arducam sensor control (OV5642)
# file: ov5642.py
# v0.01 (2025/12/29)
#

# reference
# https://github.com/ArduCAM/Arduino/blob/master/ArduCAM/ArduCAM.cpp
#

import time
from machine import I2C
from machine import Pin
from ov5642_FIFO import OV5642FIFO
from ov5642_setup import QVGA_RGB565_PREVIEW

OV5642_I2C_ADDR = 0x3c

class OV5642:

    def __init__(self, i2c, fifo_spi, fifo_spi_cs):
        self.i2c = i2c
        self.fifo = OV5642FIFO(fifo_spi, fifo_spi_cs)
        self.write_regs(QVGA_RGB565_PREVIEW)
        self.set_photo_size("QQVGA")
        self.set_flip()
    
    def start_capture(self):     #take_picture(self):
        self.fifo.flush_fifo()
        self.fifo.start_capture()
    
    def take_picture(self):
        self.fifo.take_picture()    

    def show_photo_size(self):
        hi = self.read_reg(0x3808)
        low = self.read_reg(0x3809)
        size = (hi << 8) + low
        print(f"w:{size:d} (0x{hi:02x}{low:02x})")
        hi = self.read_reg(0x380A)
        low = self.read_reg(0x380B)
        size = (hi << 8) + low
        print(f"h:{size:d} (0x{hi:02x}{low:02x})")
    
    def set_photo_size(self, size):
      if size == "QQVGA":
          self.write_reg(0x3808, 0x00)   # width:160 (0xA0)
          self.write_reg(0x3809, 0xA0)   #
          self.write_reg(0x380A, 0x00)   # height:128 (0x80)
          self.write_reg(0x380B, 0x80)   #
      else:
          print("Error not supported")
          print(size)
    
    def set_flip(self):
        self.write_reg(0x3818, 0xE1)
        self.write_reg(0x3621, 0xC7)
    
    def read_pixels(self, buf):    
        self.fifo.read_pixels(buf)    
    
    def read_reg(self, addr):   # read OV5642 REG
        try:
            return self.i2c.readfrom_mem(OV5642_I2C_ADDR, addr, 1, addrsize=16)[0]
        except Exception as e:
            print("read but failed, Except:",e)
            return None

    def write_reg(self, addr, val):   # write OV5642 REG
        try:
            self.i2c.writeto_mem(OV5642_I2C_ADDR, addr, bytes((val,)), addrsize=16)
        except Exception as e:           
            print("write but failed, Except",e)
        if addr == 0x3008 and (val & 0x80) == 0x80 :
            print('dummy read, wait for 1')
            time.sleep(1)
            val =  self.read_reg(addr)
            print('read:', val)

    #
    # arg: lst  ((addr0,val0),(addr1,val1),...,(addr_n,val_n))
    #
    def write_regs(self, lst):
        #print(f'write_regs')
        for (addr, val) in lst:
            #print(f'{addr:04x}, {val:02x}')
            self.write_reg(addr, val)
    
    
    
    
