from machine import Pin, SPI


# 50KHz
SPI_CLK=5_000_000

GP_CLK = 2
GP_MOSI = 3
GP_MISO = 4
GP_CS = 5

#
# define bit fields
#
import uctypes
DATA = {
  "tc_temp"   : 18 << uctypes.BF_POS | 14 << uctypes.BF_LEN | uctypes.BFUINT32,
  "res1"      : 17 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
  "fault_bit" : 16 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
  "int_temp"  : 4 << uctypes.BF_POS | 12 << uctypes.BF_LEN | uctypes.BFUINT32,
  "res0"      : 3 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
  "scv_bit"   : 2 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
  "scg_bit"   : 1 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
  "oc_bit"    : 0 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
}


spi = SPI(0, baudrate=SPI_CLK, polarity=0, phase=0, bits=8, sck=Pin(GP_CLK), mosi=Pin(GP_MOSI), miso=Pin(GP_MISO))
cs = Pin(GP_CS, Pin.OUT)


# >>> spi
# SPI(0, baudrate=4807692, polarity=0, phase=0, bits=8, sck=2, mosi=3, miso=4)
# >>> cs
# Pin(GPIO5, mode=OUT)


#cs.high()
#cs.low()
#spi.read(4)
#b'\x00\x00\x03\x00'

import time


#
# convert 32bit data  ->  couple_temp, inter_temp, flag2, flag1, flag0 
#
def convert(buf):
    regs = uctypes.struct(uctypes.addressof(buf), DATA, uctypes.BIG_ENDIAN)

    # check sign big
    if regs.tc_temp & 0b10_0000_0000_0000:  # if minus flag is set
         temp_2b = struct.pack('>h', regs.tc_temp >> 2)  # extract only the integer part
                                                      # and convert integer to byte array
         temp_ary = bytearray(temp_2b) 
         temp_ary[0] |= 0b1111_0000                   # Perform sign extension
         tc_temp = struct.unpack('>h',temp_ary)[0]    # convert byte array to interger
         tc_temp += ((regs.tc_temp >> 1) & 1) * 1/2 + (regs.tc_temp & 1) * 1/4
    else:
         tc_temp = regs.tc_temp >> 2
         tc_temp += ((regs.tc_temp >> 1) & 1) * 1/2 + (regs.tc_temp & 1) * 1/4
    print("tc temp:", tc_temp)

    print("inter temp:", (regs.int_temp>>4)  + ((regs.int_temp >> 3) & 1) * 1/2 +   ((regs.int_temp >> 2) & 1) * 1/4  + ((regs.int_temp >> 1) & 1) * 1/8   +   (regs.int_temp & 1) * 1/16 )


while True:
    cs.low()
    data = spi.read(4)
    print(data)
    convert(data)
    cs.high()  
    time.sleep(1)


#data = bytes((0x1,0x4,0xf,0xa0))
#buf = bytearray(4)  # 16bit width buffer
#data = bytes((0x1,0x4,0xf,0xa0))
#buf[3] = 0x01
#buf[2] = 0x04
#buf[1] = 0x0f
#buf[0] = 0xa0

