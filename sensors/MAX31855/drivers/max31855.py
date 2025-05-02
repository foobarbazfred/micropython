#
# Driver for MAX31855
#
#

#
# define bit fields
#
import uctypes
import struct
REG_BIT_FIELDS = {
   "tc_temp"   : 18 << uctypes.BF_POS | 14 << uctypes.BF_LEN | uctypes.BFUINT32,
   "res1"      : 17 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   "fault_bit" : 16 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   "int_temp"  :  4 << uctypes.BF_POS | 12 << uctypes.BF_LEN | uctypes.BFUINT32,
   "res0"      :  3 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   "scv_bit"   :  2 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   "scg_bit"   :  1 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
   "oc_bit"    :  0 << uctypes.BF_POS |  1 << uctypes.BF_LEN | uctypes.BFUINT32,
}


class MAX31855:

    def __init__(self,spi,cs,verbose=False):
        self.spi = spi
        self.cs = cs
        self.verb = verbose

    def get_temperature(self):
        self.cs.low()
        arry = self.spi.read(4)
        self.cs.high()  
        if self.verb:
            print(arry)
        (tc_temp, int_temp, scv_flag, scg_flag, oc_flag) = self._parse_data(arry)
        if scv_flag == 0 and  scg_flag == 0 and oc_flag == 0:
            status = 'OK'
        else:
            status = "ERROR"
            if scv_flag == 1:
                   status += ",SVC"
            if scg_flag == 1:
                   status += ",SCG"
            if oc_flag == 1:
                   status +=",OC"
        return (tc_temp, int_temp, status)
    
    #
    # convert 32bit data  ->  couple_temp, inter_temp, scv_flag, scg_flag, oc_flag
    #
    def _parse_data(self, arry):


        regs = uctypes.struct(uctypes.addressof(arry), REG_BIT_FIELDS, uctypes.BIG_ENDIAN)

        scv_flag = regs.scv_bit;
        scg_flag = regs.scg_bit;
        oc_flag = regs.oc_bit;

        # check flag
        if scv_flag == 0 and  scg_flag == 0 and oc_flag == 0:
              # if OK then proceed
              pass
        else:
              # if ERROR then stop convert and return with None
              return (None, None, scv_flag, scg_flag, oc_flag)

        # convert signed # bit data  to float
        # check sign bit
        tc_temp = 0
        if regs.tc_temp & 0b10_0000_0000_0000:  # if minus flag is set
             temp_2b = struct.pack('>h', regs.tc_temp >> 2)  # extract only the integer part
                                                          # and convert integer to byte array
             temp_ary = bytearray(temp_2b) 
             temp_ary[0] |= 0b1111_0000                   # Perform sign extension
             tc_temp = struct.unpack('>h',temp_ary)[0]    # convert byte array to interger
        else:
             tc_temp = regs.tc_temp >> 2

        tc_temp += ((regs.tc_temp >> 1) & 1) * 1/2 + (regs.tc_temp & 1) * 1/4
        if self.verb:
            print("tc temp:", tc_temp)

        # convert signed # bit data  to float
        # check sign bit
        int_temp = 0
        if regs.int_temp & 0b1000_0000_0000:  # if minus flag is set
             temp_2b = struct.pack('>h', regs.int_temp >> 4)  # extract only the integer part
                                                              # and convert integer to byte array
             temp_ary = bytearray(temp_2b) 
             #temp_ary[0] |= 0b1000_0000                   # no need Perform sign extension
             int_temp = struct.unpack('>h',temp_ary)[0]    # convert byte array to interger
        else:
             int_temp = regs.int_temp >> 4
        if self.verb:
            print("int temp:", int_temp)

        int_temp += ((regs.int_temp >> 3) & 1) * 1/2 + ((regs.int_temp >> 2) & 1) * 1/4 + ((regs.int_temp >> 1) & 1) * 1/8  + (regs.int_temp & 1) * 1/16

        if self.verb:
            print("inter temp:", int_temp)

        return (tc_temp, int_temp, scv_flag, scg_flag, oc_flag)


        
