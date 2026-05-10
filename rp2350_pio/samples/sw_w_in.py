import time
import rp2
import machine
from machine import Pin

GP_IN_PIN = 0
STATE_MACHINE_ID = 0

@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT)            
def sw_w_in():
    # wrap_target()    # may skip
    in_(pins, 1)       # GPIO -> ISR with  1bit shift
    push()             # ISR -> RX FIFO
    # wrap()           # may skip

# to enable 2KHz to StateMachine, set systemclock to 125MHz
machine.freq(125_000_000)
sw_pin = Pin(GP_IN_PIN, mode=Pin.IN, pull=Pin.PULL_UP)
sm = rp2.StateMachine(STATE_MACHINE_ID, sw_w_in, freq=2000, in_base=sw_pin)

sm.active(1)
prev_value = None
while True:
    if sm.rx_fifo() > 0:    
        value = sm.get()
        if prev_value != value:
            print(value)
        prev_value = value
sm.active(0)
