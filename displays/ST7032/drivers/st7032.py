#
# Driver for LCD Controller ST7032 (2025/02/11 V0.4)
#
#
# V0.1
# V0.2  add HOME
#       add KANA TBL
#       print func support 2lines
#
# V0.3  refactor to ST7032LCD class 
# V0.4  bug fix: kana convert
#       utime -> time
# V0.5  support greek characters (under developing)
#       
#

import time

LCD_ADDR = 0x3e
LCD_INIT_CMDS = ( 0x38, 0x39, 0x14, 0x73, 0x56, 0x6c, 0x38, 0x01, 0x0C )

KANA_TABLE_KEY_DAKUTEN = 'dd'
KANA_TABLE_KEY_HANDAKUTEN = 'hh'

KANA_TABLE = {
   '.' : 0xA1 , '[' : 0xA2, ']' : 0xA3,  ',' : 0xA4 , 
   '-' : 0xB0 , 

   'a' : 0xB1 , 'i' : 0xB2 , 'u' : 0xB3 , 'e' : 0xB4 , 'o' : 0xB5 , 
   'ka' : 0xB6 , 'ki' : 0xB7 , 'ku' : 0xB8 , 'ke' : 0xB9 , 'ko' : 0xBa , 
   'sa' : 0xBB , 'si' : 0xBC , 'su' : 0xBD , 'se' : 0xBE , 'so' : 0xBF , 

   'ta' : 0xC0 , 'ti' : 0xC1 , 'tu' : 0xC2 , 'te' : 0xC3 , 'to' : 0xC4 , 
   'na' : 0xC5 , 'ni' : 0xC6 , 'nu' : 0xC7 , 'ne' : 0xC8 , 'no' : 0xC9 , 
   'ha' : 0xCA , 'hi' : 0xCB , 'hu' : 0xCC , 'he' : 0xCD , 'ho' : 0xCe , 

   'ma' : 0xCF , 'mi' : 0xD0 , 'mu' : 0xD1 , 'me' : 0xD2 , 'mo' : 0xD3 , 
   'ya' : 0xD4 , 'yu' : 0xD5 , 'yo' : 0xD6 , 
   'ra' : 0xD7 , 'ri' : 0xD8 , 'ru' : 0xD9 , 're' : 0xDa , 'ro' : 0xDB , 

   'wa' : 0xDC , 'wo' : 0xA6 , 'nn' : 0xDD , 
   'xa' : 0xA7 , 'xi' : 0xA8 , 'xu' : 0xA9 , 'xe' : 0xAA , 'xo' : 0XAB , 
   'xya' : 0xAC , 'xyu' : 0xAD , 'xyo' : 0xAE ,  'xtu' : 0xAF , 

   # dd :dakuten,  hh: handakuten,  gg: nakaguro (nakaten)
   'dd' : 0xDE , 'hh' : 0xDF , 'gg' : 0xA5,      
}

DAKU_TABLE = {
   'ga' : 'ka',  'gi' : 'ki',  'gu' : 'ku',  'ge' : 'ke',  'go' : 'ko',
   'za' : 'sa',  'zi' : 'si',  'zu' : 'su',  'ze' : 'se',  'zo' : 'so',
   'da' : 'ta',  'di' : 'ti',  'du' : 'tu',  'de' : 'te',  'do' : 'to',
   'ba' : 'ha',  'bi' : 'hi',  'bu' : 'hu',  'be' : 'he',  'bo' : 'ho',
}

HANDAKU_TABLE = {
   'pa' : 'ha',  'pi' : 'hi',  'pu' : 'hu',  'pe' : 'he',  'po' : 'ho',
}

GREEK_TABLE = {
    'SECTION' :  0x12, 'RAGRAPH' : 0x13, 'GAMMA' :  0x14, 'DELTA' :  0x15,
    'THETA' :  0x16, 'LAMBDA' :  0x17, 'XI' :  0x18, 'PI' :  0x19,
    'SIGMA' :  0x1A, 'UPSILON' :  0x1B, 'PHI' :  0x1C, 'PSI' :  0x1D,
    'OMEGA' :  0x1E, 'ALPHA' :  0x1F,
}


class ST7032LCD:

    def __init__(self, i2c):

        self.i2c = i2c
        self.setup()

    def setup(self):

        time.sleep_ms(50)

        # controller connection check
        if LCD_ADDR in self.i2c.scan():
            print("LCD controller connection is ok")
        else:
            print("Error! LCD controller is not connected")
            return      

        for cmd in LCD_INIT_CMDS:
            self.i2c.writeto_mem(LCD_ADDR, 0x0, bytes((cmd,)))
            if cmd == 0x6C:
                time.sleep_ms(500)
            else:
                time.sleep_us(1000)

    def print(self, out_str, cls=False):
     
        if cls:
            self.cls()

        if '\n' in out_str:
            line0 = out_str.split('\n')[0]
            line1 = out_str.split('\n')[1]
            if line0 != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, line0.encode('ascii'))
                time.sleep_ms(100)
            self.CRLF()
            if line1 != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, line1.encode('ascii'))
                time.sleep_ms(100)
        else:
            if out_str != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, out_str.encode('ascii'))
                time.sleep_ms(100)
    
    def print_greek(self, out_str, cls=False):

        if cls:
            self.cls()

        if '\n' in out_str:
            line0 = out_str.split('\n')[0]
            line1 = out_str.split('\n')[1]
            if line0 != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, self.greek2code(line0))
                time.sleep_ms(100)
            self.CRLF()
            if line1 != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, self.greek2code(line1))
                time.sleep_ms(100)
        else:
            if out_str != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, self.greek2code(out_str))
                time.sleep_ms(100)
    

    def print_kana(self, out_str, cls=False):

        if cls:
            self.cls()

        if '\n' in out_str:
            line0 = out_str.split('\n')[0]
            line1 = out_str.split('\n')[1]
            if line0 != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, self.kana2code(line0))
                time.sleep_ms(100)
            self.CRLF()
            if line1 != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, self.kana2code(line1))
                time.sleep_ms(100)
        else:
            if out_str != '':
                self.i2c.writeto_mem(LCD_ADDR, 0x40, self.kana2code(out_str))
                time.sleep_ms(100)
    
    def CRLF(self):

        self.i2c.writeto_mem(LCD_ADDR, 0x0, bytes((0x80 + 0x40,)))
        time.sleep_ms(100)
    
    def cls(self):

        self.i2c.writeto_mem(LCD_ADDR, 0x0, bytes((0x01,)))
        time.sleep_ms(100)
    
    def home(self):

        self.i2c.writeto_mem(LCD_ADDR, 0x0, bytes((0x02,)))
        time.sleep_ms(100)

    def kana2code(self, str):

        code = bytearray(len(str))  # converted kana code is shoter than katanaka expression
        code[0] = 0
    
        src_idx = 0
        dst_idx = 0
    
        while src_idx < len(str):

            if str[src_idx : src_idx+3] in KANA_TABLE:      # if  xxx
                    code[dst_idx] = KANA_TABLE[str[src_idx : src_idx+3]]
                    src_idx += 3
                    dst_idx += 1

            elif str[src_idx : src_idx+2] in DAKU_TABLE:   # if  xx in DAKU_TABLE
                    stripped_daku_kana = DAKU_TABLE[str[src_idx : src_idx+2]]
                    code[dst_idx] = KANA_TABLE[stripped_daku_kana]
                    src_idx += 2
                    dst_idx += 1
                    code[dst_idx] = KANA_TABLE[KANA_TABLE_KEY_DAKUTEN]
                    dst_idx += 1

            elif str[src_idx : src_idx+2] in HANDAKU_TABLE:   # if  xx in HANDAKU_TABLE
                    stripped_handaku_kana = HANDAKU_TABLE[str[src_idx : src_idx+2]]
                    code[dst_idx] = KANA_TABLE[stripped_handaku_kana]
                    src_idx += 2
                    dst_idx += 1
                    code[dst_idx] = KANA_TABLE[KANA_TABLE_KEY_HANDAKUTEN]
                    dst_idx += 1

            elif str[src_idx : src_idx+2] in KANA_TABLE:      # if  xx
                    code[dst_idx] = KANA_TABLE[str[src_idx : src_idx+2]]
                    src_idx += 2
                    dst_idx += 1

            elif str[src_idx] in KANA_TABLE:     # if  x
                    code[dst_idx] = KANA_TABLE[str[src_idx]]
                    src_idx += 1
                    dst_idx += 1
            else:                           
                print(f'parse error: {str[0:src_idx]}->{str[src_idx:]}')
                break
        
        if dst_idx == 0:
            return None
        else:
            return code[0 : dst_idx]
    
    
