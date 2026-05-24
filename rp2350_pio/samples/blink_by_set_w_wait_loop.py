#
# test program blink with wait loop
#

import machine
from machine import Pin
import rp2

SET_BASE_PIN = 1           # assume LED is connected GP01
machine.freq(125_000_000)  # set 125MHz to same as RP2040
STATE_MACHINE_ID = 0
STATE_MACHINE_FREQ = 2_000  # execute StateMachine with 2KHz

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink_w_wait():
    set(pins, 1)             # GP01 <- 1
    mov(x,y)                 # x <- y (0x0300)
    label('wait_loop_0')
    jmp(x_dec,'wait_loop_0') # while x--
    set(pins, 0)             # GP01 <- 0
    mov(x,y)                 # x <- y (0x0300)
    label('wait_loop_1')
    jmp(x_dec,'wait_loop_1') # while x--

sm = rp2.StateMachine(STATE_MACHINE_ID, blink_w_wait, freq=STATE_MACHINE_FREQ, set_base=Pin(SET_BASE_PIN))

#
# get value from  scratch register [x] or [y] 
#
def get_from_scratch_reg(sm, x_or_y):
    sm.exec(f"mov(isr, {x_or_y})")
    sm.exec("push()")
    return sm.get()
#
#  set value to  scratch register [x] or [y] 
#
def set_to_scratch_reg(sm, x_or_y, val):
    sm.put(val)
    sm.exec("pull()")
    sm.exec(f"mov({x_or_y}, osr)")

#
# set a value 0x300 to register Y 
# that is for wait loop constant 
#
set_to_scratch_reg(sm, 'y', 0x0300)


#
# start StateMachine
#
sm.active(1)


