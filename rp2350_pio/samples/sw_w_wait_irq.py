import time
import rp2
import machine
from machine import Pin

GP_IN_PIN = 0
STATE_MACHINE_ID = 0

def pio_handler(sm):
    print('IRQ from SM:', sm)

@rp2.asm_pio()            
def sw_w_wait_irq():
    # wrap_target()    # may skip
    wait(0,pin,0)      # wait until GPIO 0 becomes LOW
    irq(0)             # set IRQ flag
    wait(1,pin,0)      # wait until GPIO 0 becomes HIGH
    # wrap()           # may skip

# to enable 2KHz to StateMachine, set systemclock to 125MHz
machine.freq(125_000_000)
sw_pin = Pin(GP_IN_PIN, mode=Pin.IN, pull=Pin.PULL_UP)
sm = rp2.StateMachine(STATE_MACHINE_ID, sw_w_wait_irq, freq=2000, in_base=sw_pin)
sm.irq(handler=pio_handler)

sm.active(1)
time.sleep(10)
sm.active(0)
