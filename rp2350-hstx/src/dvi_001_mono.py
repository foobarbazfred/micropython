#
# git hub version file: dvi_001_mono.py
#
#  V0.01  (2026/8/9)
#   monochrome version
#   DVI size: 640x480
#

import time
import machine
from rp2 import DMA
import array

from mylib import write_reg
from mylib import write_CLK_HSTX_CTRL
from mylib import write_CLK_HSTX_DIV
from mylib import write_HSTX_CTRL_CSR
from mylib import write_HSTX_CTRL_BIT
from mylib import write_HSTX_CTRL_EXPAND_TMDS
from mylib import write_HSTX_CTRL_EXPAND_SHIFT


C1C0_BLANK = 0x354
C1C0_HSYNC = 0x0AB
C1C0_VSYNC = 0x154
C1C0_HVSYNC = 0x2AB

#
# connection of DVI Socket Board
# https://github.com/wren6991/pico-dvi-sock
#
# bit0 /  D0+  / GP12   Blue
# bit1 /  D0-  / GP13   Blue
#
# bit2 /  CLK+ / GP14   CLK
# bit3 /  CLK- / GP15   CLK
#
# bit4 /  D2+  / GP16   Red 
# bit5 /  D2-  / GP17   Red
#
# bit6 /  D1+  / GP18   Green
# bit7 /  D1-  / GP19   Green


# Front PORCH
#   (BLANK*16 + HSYNC*96 + BLANK*48 + BLANK*640) * 10
#
# VSYNC
#   (VSYNC*16 + HHSYNC*96 + VSYNC*48 + VSYNC*640) * 2
#
# Back PORCH
#   (BLANK*16 + HSYNC*96 + BLANK*48 + BLANK*640) * 33
#
# Display Lines
#  (BLANK*16 + HSYNC*96 + BLANK*48 + disp_area*640) * 480


# 32bit pack (R(10bit):G(10bit):B(10bit))
PACK_BLANK = C1C0_BLANK << 20 | C1C0_BLANK << 10 | C1C0_BLANK
PACK_HSYNC = C1C0_BLANK << 20 | C1C0_BLANK << 10 | C1C0_HSYNC
PACK_VSYNC = C1C0_BLANK << 20 | C1C0_BLANK << 10 | C1C0_VSYNC
PACK_HVSYNC = C1C0_BLANK << 20 | C1C0_BLANK << 10 | C1C0_HVSYNC


#
# set system clock 126MHz
#

machine.freq(126_000_000)



#
# setup GPIO (GP12-GP19)
#

# select function as HSTX
# 9.11.1. IO - User Bank P592
BASE_IO_BANK0 = 0x40028000
set_val = 0x0  # select HSTX
for gp_no in range(12,20):
    write_reg(BASE_IO_BANK0, gp_no * 8 + 4, set_val)

# setup PAD
# 9.11.3. Pad Control - User Bank P771
BASE_PADS_BANK0 = 0x40038000
set_val = 0x10  # ISO:0, IE:0, DRIVE:0x1(4mA), PUE:0, PDE:0,
for gp_no in range(12,20):
    write_reg(BASE_PADS_BANK0, gp_no * 4 + 4, set_val)


#
#
# Clock Setup
#
#

CLK_ENABLE = 1
CLK_SYS = 0

# SYS_CLK
CLK_ENABLE = 1
CLK_SYS = 0
val = (CLK_ENABLE << 11) + (CLK_SYS << 5)
write_CLK_HSTX_CTRL(0)  # disable clock
div = 1 << 16
write_CLK_HSTX_DIV(div)   # 150 MHz
write_CLK_HSTX_CTRL(val)  # enable and PLL source


#
# HSTX SETUP
#

#
# EXPAND SHIFT
#
# EXPAND_SHIFT
# RAW_SHIFT: 32
# RAW_N_SHIFTS: 1

RAW_SHIFT = 0       # 0 means 32
RAW_N_SHIFTS = 1

# encoded expand
# each 16bit (RGB:565) and 2times
#
ENC_SHIFT=1
ENC_N_SHIFTS=0  # N_SHIFT 0 means 32
#
#
val = ENC_N_SHIFTS << 24 | ENC_SHIFT << 16 |RAW_N_SHIFTS << 8 | RAW_SHIFT
write_HSTX_CTRL_EXPAND_SHIFT(val)


#
# EXPAND TMDS  MONO COLOR

l0_nbits = 0
l0_rot = 25
l1_nbits = l0_nbits
l1_rot = l0_rot
l2_nbits = l0_nbits
l2_rot = l0_rot

val = l2_nbits << 21 | l2_rot << 16 | l1_nbits << 13 |  l1_rot << 8 |  l0_nbits << 5 |  l0_rot 
write_HSTX_CTRL_EXPAND_TMDS(val)


#
# setup BIT
#


INV_FLG = 1
OFFSET_INV_BIT = 16
CLK_FLG = 1
OFFSET_CLK_BIT = 17

# BIT0
nth_bit = 0
sel_p = 0
sel_n = sel_p + 1
val = sel_n << 8 | sel_p
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT1
nth_bit = 1
val |= INV_FLG << OFFSET_INV_BIT
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT2
nth_bit = 2
val = CLK_FLG << OFFSET_CLK_BIT
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT3
nth_bit = 3
val |= INV_FLG << OFFSET_INV_BIT
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT4
nth_bit = 4
sel_p = 20
sel_n = sel_p + 1
val = sel_n << 8 | sel_p
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT5
nth_bit = 5
val |= INV_FLG << OFFSET_INV_BIT
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT6
nth_bit = 6
sel_p = 10
sel_n = sel_p + 1
val = sel_n << 8 | sel_p
write_HSTX_CTRL_BIT(nth_bit, val)

# BIT7
nth_bit = 7
val |= INV_FLG << OFFSET_INV_BIT
write_HSTX_CTRL_BIT(nth_bit, val)


#
#
#

CLK_DIV=5
N_SHIFTS = 5
SHIFT = 2
val =  CLK_DIV << 28 | N_SHIFTS << 16 | SHIFT << 8 | 0x3
write_HSTX_CTRL_CSR(val)


#------------------------------------------------------------------------
#  setup done
#------------------------------------------------------------------------


#
# create VGA Buffer
#

VGA_WIDTH=640
VGA_HEIGHT=480


# mono color

pixel_pattern = 0b1111_0000_1100_1100_1010_1010_1111_1111

def init_vga_data():

    data_size = 6 * 10 +  6 * 2 + 6 * 33 + 8 * VGA_HEIGHT

    buffer = array.array('I', [0] * data_size)  # I means unsigned int
    index = 0

    # setup pre  BLANK * n + HSYNC * n + BLANK * n + BLANK * VGA_WIDTH
    for _ in range(10):
        buffer[index] = 0x00_00_10_00 + 16
        index += 1
        buffer[index] = PACK_BLANK
        index += 1
        buffer[index] = 0x00_00_10_00 + 96
        index += 1
        buffer[index] = PACK_HSYNC
        index += 1
        buffer[index] = 0x00_00_10_00 + (48 + VGA_WIDTH)
        index += 1
        buffer[index] = PACK_BLANK
        index += 1

    # setup pre  BLANK * n + HSYNC * n + BLANK * n + BLANK * VGA_WIDTH
    for _ in range(2):
        buffer[index] = 0x00_00_10_00 + 16
        index += 1
        buffer[index] = PACK_VSYNC
        index += 1
        buffer[index] = 0x00_00_10_00 + 96
        index += 1
        buffer[index] = PACK_HVSYNC
        index += 1
        buffer[index] = 0x00_00_10_00 + (48 + VGA_WIDTH)
        index += 1
        buffer[index] = PACK_VSYNC
        index += 1

    # setup pre  BLANK * n + HSYNC * n + BLANK * n + BLANK * VGA_WIDTH
    for _ in range(33):
        buffer[index] = 0x00_00_10_00 + 16
        index += 1
        buffer[index] = PACK_BLANK
        index += 1
        buffer[index] = 0x00_00_10_00 + 96
        index += 1
        buffer[index] = PACK_HSYNC
        index += 1
        buffer[index] = 0x00_00_10_00 + (48 + VGA_WIDTH)
        index += 1
        buffer[index] = PACK_BLANK
        index += 1

    #
    # image area (640x480)
    # setup pre  BLANK * n + HSYNC * n + BLANK * n + BLANK * VGA_WIDTH
    for _ in range(VGA_HEIGHT):
        buffer[index] = 0x00_00_10_00 + 16
        index += 1
        buffer[index] = PACK_BLANK
        index += 1
        buffer[index] = 0x00_00_10_00 + 96
        index += 1
        buffer[index] = PACK_HSYNC
        index += 1
        buffer[index] = 0x00_00_10_00 + 48
        index += 1
        buffer[index] = PACK_BLANK
        index += 1

        # DISPLAY DATA
        buffer[index] = 0x00_00_30_00 + VGA_WIDTH
        index += 1
        buffer[index] = pixel_pattern
        index += 1

    return buffer

#
# create buffer for VGA display
#
vga_buffer = init_vga_data()
buffer_size = len(vga_buffer)

#
# setup DMA
#
#  dreq:  DREQ_HSTX(52)
#

dma0 = DMA()
dma1 = DMA()


prev_0 = 0
current_0 = 0
counter_0 = 0

DBG = False

def dma0_itr_handler(arg):
    if DBG:
        global prev_0
        global current_0
        global counter_0

    dma0.read = vga_buffer

    if DBG:
        #print('.',end='')
        counter_0 += 1
        current_0 = time.ticks_us()
        if counter_0 % 60 == 0:
            counter_0 = 0
            print(time.ticks_diff(current_0, prev_0))
        prev_0 = current_0


def dma1_itr_handler(arg):
    dma1.read = vga_buffer

def setup_dma(dma0,dma1,buffer, buffer_size):

    BASE_HTSX_FIFO = 0x5060_0000
    HSTX_FIFO_ADDR = BASE_HTSX_FIFO + 0x4
    
    dma0.irq(handler=dma0_itr_handler, hard=True)
    dma1.irq(handler=dma1_itr_handler, hard=True)

    dma0_ctrl = dma0.pack_ctrl(size=2, inc_read=True, inc_write=False, treq_sel=52, irq_quiet=False, chain_to=dma1.channel)
    dma0.config(read=buffer, write=HSTX_FIFO_ADDR, ctrl=dma0_ctrl, trigger=False, count=buffer_size)

    dma1_ctrl = dma1.pack_ctrl(size=2, inc_read=True, inc_write=False, treq_sel=52, irq_quiet=False, chain_to=dma0.channel)
    dma1.config(read=buffer, write=HSTX_FIFO_ADDR, ctrl=dma1_ctrl, trigger=False, count=buffer_size)
                                                                                           

setup_dma(dma0, dma1, vga_buffer, buffer_size)


# start to generate DVI signal
dma0.active(True)

