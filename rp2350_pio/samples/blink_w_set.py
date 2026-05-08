import time
import rp2
import machine
from machine import Pin

GP_SET_PIN=1
STATE_MACHINE_ID=0

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink_w_set():
    # wrap_target()    #  may skip
    set(pins, 1)
    set(pins, 0)
    # wrap()           # may skip


# to enable 2KHz to StateMachine, set systemclock to 125MHz
machine.freq(125_000_000)

sm = rp2.StateMachine(STATE_MACHINE_ID, blink_w_set, freq=2000, set_base=Pin(GP_SET_PIN))

sm.active(1)
time.sleep(5)
sm.active(0)
