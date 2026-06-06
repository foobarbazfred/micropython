import micropython
import time
import rp2
import machine
from machine import Pin

GP_IN_PIN = 0
STATE_MACHINE_ID = 0

counter = 0

#
# Schedule pio_handler_scheduled to run in the main context when an IRQ occurs
#
def pio_handler(intr_sm):
    micropython.schedule(pio_handler_scheduled, intr_sm)

#
# execute pio_handler_scheduled() in main context
#
def pio_handler_scheduled(intr_sm):
    global counter
    print('IRQ from SM:', intr_sm)
    if intr_sm == sm0:
        print('--------------------')
        print('IRQ_SM0 is set')
        counter += 1
        print(f'counter: {counter}')
    else:
        print('IRQ_SM0 is not set')    


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
sm0 = rp2.StateMachine(STATE_MACHINE_ID, sw_w_wait_irq, freq=2000, in_base=sw_pin)
sm0.irq(handler=pio_handler)

print('start Statemachine')
sm0.active(1)
time.sleep(10)
sm0.active(0)
print('stopped Statemachine')


#
#
#