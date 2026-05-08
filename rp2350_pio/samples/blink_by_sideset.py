import time
import rp2
from machine import Pin

GP_SIDESET_PIN=1
STATE_MACHINE_ID=0

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def blink_w_sideset():
    nop() .side(0)
    nop() .side(1)

sm = rp2.StateMachine(STATE_MACHINE_ID, blink_w_sideset, freq=2000, side_base=Pin(GP_SIDESET_PIN))

sm.active(1)
time.sleep(5)
sm.active(0)
