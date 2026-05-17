import time
import rp2
import machine
from machine import Pin

GP_OUT_PIN = 1
STATE_MACHINE_ID = 0

@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT)
def blink_w_out():
    # wrap_target()    # may skip
    pull()             # TX FIFO -> OSR
    out(pins, 1)       # OSR -> GPIO  with  1bit shift
    # wrap()           # may skip


# to enable 2KHz to StateMachine, set systemclock to 125MHz
machine.freq(125_000_000)
sm = rp2.StateMachine(STATE_MACHINE_ID, blink_w_out, freq=2000, out_base=Pin(GP_OUT_PIN))

sm.active(1)
while True:
    sm.put(0x8000_0000)  # set 0x8000_0000 to TX FIFO
    sm.put(0)            # set 0 to TX FIFO
sm.active(0)
