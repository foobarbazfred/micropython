#
# arducam FIFO control (OV5642) 
# file: ov5642_FIFO.py
# v0.01 (2025/12/29)
#
from machine import Pin

FIFO_REGS=(0x00, 0x01,  0x03, 0x04,  0x06, 0x3c, 0x3d,  0x40, 0x41, 0x42, 0x43, 0x44, )
FIFO_REG_NAMES=('TEST     ','CaptCtrl ','TimReg   ','FIFO Ctrl','GPIO Wr  ','FIFO     ','FIFO     ','FirmV    ','SyncCap  ','FIFO_L   ','FIFO_M   ','FIFO_H   ')



FIFO_CTRL_REG = 0x04
CAMERA_STATUS_REG = 0x41
BURST_FIFO_READ_REG = 0x3c
SIGLE_FIFO_READ_REG = 0x3d

FIFO_CLEAR_DONE_BIT = 0x01
FIFO_START_BIT = 0x02
FIFO_WRPTR_RST_BIT = 0x10
FIFO_RDPTR_RST_BIT = 0x20


FIFO_REG_WRITE_FLAG = 0x80
CAPTURE_DONE_FLAG = 0x08

#
# usage
#
# spi = TFTSetup.hspi
# cs = Pin(15, Pin.OUT)
#
#  fifo = OV5642FIFO(spi, cs)


class OV5642FIFO:

    def __init__(self, spi, cs):
       self.spi = spi   
       self.cs = cs
       self.setup_FIFO()

    def setup_FIFO(self):
        self.reset_FIFO()

    def start_capture(self):
        self.write_reg(FIFO_CTRL_REG, FIFO_START_BIT)

    def clear_done_flag(self):
        self.write_reg(FIFO_CTRL_REG, FIFO_CLEAR_DONE_BIT)

    def reset_FIFO(self):
        self.reset_FIFO_read_pointer()
        self.reset_FIFO_write_pointer()

    def reset_FIFO_read_pointer(self):
        self.write_reg(FIFO_CTRL_REG, FIFO_RDPTR_RST_BIT)
    
    # set FIFO write pointer to 0
    # and side effect, start capture 
    def reset_FIFO_write_pointer(self):
        self.write_reg(FIFO_CTRL_REG, FIFO_WRPTR_RST_BIT)
    
    def start_capture_and_wait(self):
        self.clear_done_flag()
        self.start_capture() 
        # wait until set 'camera capture done flag'
        done_flag = 0 
        while not (done_flag & CAPTURE_DONE_FLAG):
            done_flag = self.read_reg(CAMERA_STATUS_REG)

    def show_sync(self):
        prev_flag = self.read_reg(CAMERA_STATUS_REG)
        while True:
            flag = self.read_reg(CAMERA_STATUS_REG)
            if (prev_flag & 1) == 1 and (flag & 1) == 0:
                   print("[sync]", end="")
    
    def dump_img(self):
        for i in range(256):
            val = self.read_reg(SIGLE_FIFO_READ_REG)     # single FIFO read
            print("{:02x} ".format(val), end="")
            if (i + 1) % 16 == 0:
                print("")
    
    def show_regs(self):
        for i in range(len(FIFO_REGS)):
            addr = FIFO_REGS[i]
            name = FIFO_REG_NAMES[i]
            print("{:s}(0x{:02x}): ".format(name, addr), end="")
            print("{:02x}".format(self.read_reg(addr)))
    
    def read_pixels(self, buf):
        self.cs.off()
        self.spi.write(bytes((BURST_FIFO_READ_REG,)))      # burst FIFO read
        self.spi.readinto(buf)
        self.cs.on()

    def read_reg(self, addr):
        self.cs.off()
        self.spi.write(bytes((addr,)))
        val = self.spi.read(1)[0]
        self.cs.on()
        return val
    
    def write_reg(self, addr, val):
        self.cs.off()
        self.spi.write(bytes((addr | FIFO_REG_WRITE_FLAG,)))
        self.spi.write(bytes((val,)))
        self.cs.on()
    

