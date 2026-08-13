#
# file: dvi_008_mono.py   
# monochrome display (black/white) with using frame buffer (640x480 dot)
#
#  V0.01  (2026/8/12)
#   monochrome version
#   display size: DVI (640x480)
#   display pattern: test stripes with black/white
#   using 5 DMAs, 
#      DMA0 : transfer VSYNC
#      DMA1 : transfer HSYNC 
#      DMA2 : transfer DISPLAY DATA
#      DMA10 : notify PIO if trigger by DMA1
#      DMA11 : get ctrl_params from PIO and set DMA2
#   using 1 PIO for count display line and switch chain of DMA2 
#  V0.02  (2026/8/12 21:05)
#    bug fix: Controller for TMDS with length is missing, so fix it
#    N_OF_PIXELS = 32   # 32pixels in 1 data
#    def setup_vga_display(buffer):
#                     *skip*
#             buffer[index] = 0x00_00_20_00 + N_OF_PIXELS
#
#  V0.03  (2026/8/13 20:20)
#     bug fix: function make_aligned_buffer is address caclate miss, fix it 
#

import time
import machine
import rp2
from rp2 import DMA
from array import array
from machine import Pin


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
#
# SYS_CLK
#
CLK_ENABLE = 1
CLK_SYS = 0
CLK_PLL_USB=2
val = (CLK_ENABLE << 11) + (CLK_SYS << 5)    # DVI Speed
#val = (CLK_ENABLE << 11) + (CLK_PLL_USB << 5)  # slow speed for debug
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


from uctypes import addressof


def is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0

#
# create alligned buffer
# array type is WORD(32bit) only
# size is n of words (not bytes)
# so in memory area, allocating address is n * 4
#
def make_aligned_buffer(word_size):

    if is_power_of_two(word_size):
         pass
    else:
         print('internal error! not power of 2')
         return None

    buffer = array('I', [0] * word_size * 2)  # I means unsigned int
    base_addr = addressof(buffer)
    if base_addr == (base_addr  &  ~(word_size * 4 - 1)):
        target_addr = base_addr
    else:
        target_addr = (base_addr  &  ~(word_size * 4 - 1)) + word_size * 4
    offset_index = int((target_addr - base_addr) / 4)
    print(offset_index, word_size)
    return memoryview(buffer)[offset_index : offset_index + word_size]

#
# create simple buffer
# array type is WORD(32bit) only
#
def make_simple_buffer(size):

    buffer = array('I', [0] * size)  # I means unsigned int
    return buffer



# size:8
def setup_vga_HSYNC(buffer):

    index = 0
    buffer[index] = 0x00_00_10_00 + 8
    index += 1
    buffer[index] = PACK_BLANK
    index += 1
    buffer[index] = 0x00_00_10_00 + 8
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



def setup_vga_VSYNC(buffer):

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


# mono color
pixel_pattern = 0b1111_0000_1100_1100_1010_1010_1111_1111
N_OF_PIXELS = 32   # 32pixels in 1 data
def setup_vga_display(buffer):

    #
    # image area (640x480)
    # setup pre  BLANK * n + HSYNC * n + BLANK * n + BLANK * VGA_WIDTH
    index = 0
    for _ in range(int(VGA_WIDTH / 32) * VGA_HEIGHT):
        # DISPLAY DATA
        buffer[index] = 0x00_00_20_00 + N_OF_PIXELS
        index += 1
        buffer[index] = pixel_pattern
        index += 1

    return buffer


vsync_data_size = 6 * 10 +  6 * 2 + 6 * 33   # 
vsync_frame_buffer = make_simple_buffer(vsync_data_size)
setup_vga_VSYNC(vsync_frame_buffer)

hsync_data_size = 8    #  8 WORD (4bytes * 8)
hsync_frame_buffer = make_aligned_buffer(hsync_data_size)
setup_vga_HSYNC(hsync_frame_buffer)

#
# /32 means  array of 1data(32bit) -> 32 pixel data
#
disp_data_size = int(VGA_WIDTH / 32 ) * VGA_HEIGHT * 2
disp_frame_buffer =  make_simple_buffer(disp_data_size)
dummy = setup_vga_display(disp_frame_buffer)  # to avoid show vars


#############
#  for debug (monitoring by monitor pin with an Osciloscope)
from machine import Pin
gp0 = Pin(0, Pin.OUT)
gp1 = Pin(1, Pin.OUT)
gp2 = Pin(2, Pin.OUT)

gp0.low()
gp1.low()
gp2.low()

#########################################################
#
# setup DMA
#
#  dreq:  DREQ_HSTX(52)
#

dma0 = DMA()  # VSYNC
dma1 = DMA()  # HSYNC
dma2 = DMA()  # DISPLAY


prev_0 = 0
current_0 = 0
counter_0 = 0

DBG = False

drawing_line = 0
def dma0_itr_handler(arg):
    gp0.high()
    #global drawing_line
    #drawing_line = 0
    dma0.read = vsync_frame_buffer
    gp0.low()

# every HSYNC
drawing_line = 0
def dma1_itr_handler(arg):
    gp1.high()
    #global drawing_line
    #drawing_line += 1
    gp1.low()


# interrupt from dma2
# when drawing 480 lines then cause interrupt
last_frame_addr = 0
def dma2_itr_handler(arg):
    gp2.high()
    global last_frame_addr
    #print('D',end='')
    #global drawing_line
    last_frame_addr = dma2.read
    dma2.read = disp_frame_buffer
    dma2.ctrl = dma2_ctrl_loop
    gp2.low()


BASE_HTSX_FIFO = 0x5060_0000
HSTX_FIFO_ADDR = BASE_HTSX_FIFO + 0x4

TREQ_HSTX = 52

#
# setup DMA0  for VSYNC
#
def setup_dma0(dma0, chain_to_dma, buffer):

    dma0.irq(handler=dma0_itr_handler, hard=True)

    dma0_ctrl = dma0.pack_ctrl(size=2, inc_read=True, inc_write=False, treq_sel=TREQ_HSTX, irq_quiet=False, chain_to=chain_to_dma.channel) 

    dma0.config(read=buffer, write=HSTX_FIFO_ADDR, ctrl=dma0_ctrl, trigger=False, count=len(buffer))

#
# setup DMA1 for 
# HSYNC (ring)  must setting RING!!
#
def setup_dma1(dma1, chain_to_dma, buffer):

    dma1.irq(handler=dma1_itr_handler, hard=True)

    # ring_size : 5  (2 ** 5 )  (8 * 4 = 32)(2 **5 = 32) yueni 5

    dma1_ctrl = dma1.pack_ctrl(size=2, inc_read=True, inc_write=False, treq_sel=TREQ_HSTX, irq_quiet=False, chain_to=chain_to_dma.channel, ring_size=5, ring_sel=False)
    dma1.config(read=buffer, write=HSTX_FIFO_ADDR, ctrl=dma1_ctrl, trigger=False, count=len(buffer))
                                                                                           

#
# setup DMA1 for DISPLAY AREA
#  HSYNC->DISP->HSYNC->DISP->....
#
def setup_dma2(dma2, chain_to_dma, buffer):
    
    dma2.irq(handler=dma2_itr_handler, hard=True)

    dma2_ctrl = dma2.pack_ctrl(size=2, inc_read=True, inc_write=False, treq_sel=TREQ_HSTX, irq_quiet=False, chain_to=chain_to_dma.channel) 

    dma2.config(read=buffer, write=HSTX_FIFO_ADDR, ctrl=dma2_ctrl, trigger=False, count=int(VGA_WIDTH/32) *2 )  # /32 means omoncolor,  in 1 data(32) contains 32pixcel,  * 2 means  control + IMAGE


setup_dma0(dma0, dma1, vsync_frame_buffer)
setup_dma1(dma1, dma2, hsync_frame_buffer)
setup_dma2(dma2, dma0, disp_frame_buffer)




#
#
#


#
# dvi line counter by PIO and DMA
#
#  count 640 and write control data to FIFO 
#  collect action checked
#

#


#
# helper function for access registers
#
def read_reg(base, offset):
    return machine.mem32[base + offset]

def write_reg(base, offset, value):
    machine.mem32[base + offset] = value
#
#
#


#
# caution: overwrite ISR and RX-FIFO
#
def get_from_ISR(sm):
    sm.exec("push()")
    return sm.get()

#
#  set value to  scratch [x] or [y] 
#
def put_to_scratch_reg(sm, x_or_y, val):
    sm.put(val)
    sm.exec("pull()")
    sm.exec(f"mov({x_or_y}, osr)")

def get_from_scratch_reg(sm, x_or_y='y'):
    sm.exec(f"mov(isr, {x_or_y})")
    return get_from_ISR(sm)


#
# PIO assmbled code for 480 counter
#

@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT)
def sm_inst_count480():
    set(x, 15)      #  x <- 15 
    mov(isr, x)     #  ISR <- X
    in_(null, 5)    #  OSR LSL:5  480
    mov(x, isr)     #  X <- ISR (480) 
    #set(x,3)       # for debug
    jmp(x_dec, 'NEXT')
#NEXT:
    label('NEXT')
#WAIT_ONE_LINE:
    label('WAIT_ONE_LINE')
    pull(block)    # get value from TX FIFO w/block
    jmp(x_dec, 'WAIT_ONE_LINE')
    mov(isr, y)    # ISR <- Y
    push(block)
    
STATE_MACHINE_ID=0

# create Statemachine and code is nop
sm0 = rp2.StateMachine(STATE_MACHINE_ID, sm_inst_count480)  # , freq=2000)

put_to_scratch_reg(sm0, 'x', 0)
put_to_scratch_reg(sm0, 'y', 0xFF_00_FF_00)


#
# DMA for transfer to PIO's FIFO
#
from array import array
from rp2 import DMA

dummy_value = array('I', (1,))
dma10 = DMA()
dma10_ctrl = dma10.pack_ctrl(inc_read = False, inc_write = False)
dma10.config(read=dummy_value, write=sm0, count=1, ctrl=dma10_ctrl, trigger=False)


#
# DMA for transfer from PIO's FIFO to DMA(for display data send) control register
# write address is temprary settting  overwrite after
# 
DREQ_PIO0_RX0=4
virtual_tmp_register  = array('I', (0xFFFF_FFFF,))
dma11 = DMA()
dma11_ctrl = dma11.pack_ctrl(inc_read = False, inc_write = False, treq_sel=DREQ_PIO0_RX0)
dma11.config(read=sm0, write=virtual_tmp_register, count=1, ctrl=dma11_ctrl, trigger=False)


#
# set dma11 as ENDLESS  loop    (0xF:ENDLESS)
#

OFFSET_CH3_TRANS_COUNT=0x0c8
BASE_DMA=0x5000_0000

count_value = (0xF << 28) + 1  # transfer size:1
dma11.count = count_value
#write_reg(BASE_DMA, OFFSET_CH3_TRANS_COUNT,count_value)


#
# connect DMA/PIO
#
#
# dma0 --chain--> dma1
# dma1 --chain--> dma10
# dma10 --chain--> dma2
# dma2 --chain--> dma1
#
def set_chain_to(dma_tgt, dma_dest):
   ctrl_dic = dma_tgt.unpack_ctrl(dma_tgt.ctrl)
   ctrl_dic['chain_to'] = dma_dest.channel
   dma_tgt.ctrl = dma_tgt.pack_ctrl(**ctrl_dic)


set_chain_to(dma0,dma1)
set_chain_to(dma1,dma10)
set_chain_to(dma10,dma2)
set_chain_to(dma2,dma1)


#
# create ctrl setting data for dma2
#
dma2_ctrl_dic = dma2.unpack_ctrl(dma2.ctrl)
dma2_ctrl_dic['chain_to'] = dma1.channel
#dma2_ctrl_dic['irq_quiet'] = True

# params for loop
dma2_ctrl_dic['chain_to'] = dma1.channel
dma2_ctrl_dic['irq_quiet'] = True
dma2_ctrl_loop = dma2.pack_ctrl(**dma2_ctrl_dic)

# params for begin
dma2_ctrl_dic['chain_to'] = dma0.channel
dma2_ctrl_dic['irq_quiet'] = False
dma2_ctrl_begin = dma2.pack_ctrl(**dma2_ctrl_dic)

# params for stop
dma2_ctrl_dic['chain_to'] = dma2.channel
dma2_ctrl_dic['irq_quiet'] = False
dma2_ctrl_stop = dma2.pack_ctrl(**dma2_ctrl_dic)


# set update data to sm0 for dma2
OFFSET_AL1_CTRL = 0x10
put_to_scratch_reg(sm0, 'y', dma2_ctrl_begin)
dma11.write = BASE_DMA + 0x40 * dma2.channel + OFFSET_AL1_CTRL

#
#
dma2.ctrl = dma2_ctrl_loop

#
#
# start
#
#

# start to generate DVI signal
dma11.active(True)

# start StateMachine
sm0.active(1)

dma0.active(True)

