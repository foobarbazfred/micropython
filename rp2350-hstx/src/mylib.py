#
# helper functions for r/w registers
#


import machine

BASE_USER_BANK_IO = 0x40028000
OFFSET_GPIO16_STATUS = 0x080
OFFSET_GPIO16_CTRL = 0x084

# PADS_BANK0: GPIO16 Register


BASE_PADS_BANK0 = 0x40038000
# (defined as PADS_BANK0_BASE in SDK).
OFFSET_PADS_BANK0_GPIO16 = 0x44  # bits 8: ISO


def write_reg(base, offset, value):
    machine.mem32[base + offset] = value

def read_reg(base, offset):
    return machine.mem32[base + offset]

def read_GPIO16_STATUS_register():
    return read_reg(BASE_USER_BANK_IO, OFFSET_GPIO16_STATUS)

def read_GPIO16_CTRL_register():
    return read_reg(BASE_USER_BANK_IO, OFFSET_GPIO16_CTRL)

def write_GPIO16_CTRL_register(value):
    return write_reg(BASE_USER_BANK_IO, OFFSET_GPIO16_CTRL, value)

def read_PADS_BANK0_GPIO_register(gp_no):
    return read_reg(BASE_PADS_BANK0, 4*gp_no + 0x04)


# 0x40028000 (defined as IO_BANK0_BASE in SDK).

def write_GPIO_CTRL_register(gp_no, value):
    base = BASE_USER_BANK_IO
    offset = 8 * gp_no + 0x004
    return write_reg(base, offset, value)

def read_GPIO_CTRL_register(gp_no):
    base = BASE_USER_BANK_IO
    offset = 8 * gp_no + 0x004
    return read_reg(base, offset)


BASE_PADS_BANK0 = 0x40038000   # P771
ISO_OFFSET = 8
def clr_PADS_BANK0_GPIO_ISO(gp_no):
    base = BASE_PADS_BANK0
    offset = 4 * gp_no + 0x04
    reg_val = read_PADS_BANK0_GPIO(gp_no)
    reg_val = (~ (1 << ISO_OFFSET) & 0xFFFF_FFFF) & reg_val
    write_reg(base,offset,reg_val)

def read_PADS_BANK0_GPIO(gp_no):
    base = BASE_PADS_BANK0
    offset = 4 * gp_no + 0x04
    reg_val = read_reg(base,offset)
    return reg_val  

def write_PADS_BANK0_GPIO(gp_no,val):
    base = BASE_PADS_BANK0
    offset = 4 * gp_no + 0x04
    reg_val = write_reg(base,offset,val)
    return reg_val  


#
# HSTX_CTRL_BIT_N
#
BASE_HTSX_CTRL = 0x400c_0000

def write_HSTX_CTRL_BIT(nth_bit, val):
    base = BASE_HTSX_CTRL
    offset = 4 * (nth_bit + 1)
    write_reg(base, offset, val)

def read_HSTX_CTRL_BIT(nth_bit):
    base = BASE_HTSX_CTRL
    offset = 4 * (nth_bit + 1)
    return read_reg(base, offset)


#
# HSTX_CTRL_CSR
#
BASE_HTSX_BTRL = 0x400c_0000

def write_HSTX_CTRL_CSR(value):
    base = BASE_HTSX_CTRL
    offset = 0
    write_reg(base, offset, value)

def read_HSTX_CTRL_CSR():
    base = BASE_HTSX_CTRL
    offset = 0
    return read_reg(base, offset)


def set_HSTX_CTRL_CSR_EN():
    val = read_HSTX_CTRL_CSR()
    val |= 1
    write_HSTX_CTRL_CSR(val)

BASE_HTSX_FIFO = 0x5060_0000
def write_HSTX_FIFO(value):
    base = BASE_HTSX_FIFO
    offset = 0x4
    write_reg(base, offset, value)
    

def read_HSTX_FIFO_stat():
    base = BASE_HTSX_FIFO
    offset = 0
    return read_reg(base, offset)


#0x400c0000 (defined as HSTX_CTRL_BASE in
OFFSET_EXPAND_SHIFT=0x24
def write_HSTX_CTRL_EXPAND_SHIFT(val):
    base = BASE_HTSX_CTRL
    offset = OFFSET_EXPAND_SHIFT
    return write_reg(base, offset,val)
    
def read_HSTX_CTRL_EXPAND_SHIFT():
    base =  BASE_HTSX_CTRL
    offset = OFFSET_EXPAND_SHIFT
    return read_reg(base, offset)
    

OFFSET_EXPAND_TMDS=0x28
def write_HSTX_CTRL_EXPAND_TMDS(val):
    base = BASE_HTSX_CTRL
    offset = OFFSET_EXPAND_TMDS
    return write_reg(base, offset,val)

def read_HSTX_CTRL_EXPAND_TMDS():
    base =  BASE_HTSX_CTRL
    offset = OFFSET_EXPAND_TMDS
    return read_reg(base, offset)
    

BASE_CLOCKS = 0x40010000 
OFFSET_CLK_HSTX_CTRL = 0x54
OFFSET_CLK_HSTX_DIV = 0x58


def read_CLK_HSTX_CTRL():
    base = BASE_CLOCKS
    offset = OFFSET_CLK_HSTX_CTRL
    return read_reg(base, offset)
    
def write_CLK_HSTX_CTRL(val):
    base = BASE_CLOCKS
    offset = OFFSET_CLK_HSTX_CTRL
    return write_reg(base, offset,val)
    
def read_CLK_HSTX_DIV():
    base = BASE_CLOCKS
    offset = OFFSET_CLK_HSTX_DIV
    return read_reg(base, offset)
    
def write_CLK_HSTX_DIV(val):
    base = BASE_CLOCKS
    offset = OFFSET_CLK_HSTX_DIV
    return write_reg(base, offset,val)
    


# >>> hex(read_CLK_HSTX_DIV())
# '0x10000'
# >>> 160 * 1000 / 65536
# 2.4414062
# 2KHz

BASE_RESETS = 0x40020000
OFFSET_RESETS_RESET = 0
def read_RESETS_RESET():
    base = BASE_CLOCKS
    offset = OFFSET_RESETS_RESET
    return read_reg(base, offset)

