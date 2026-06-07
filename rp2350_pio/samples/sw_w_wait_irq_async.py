#
# PIO Sample
#
#  - input 1bit 
#  - use irq
#  - execute with asyncio 
#
import micropython
import time
import asyncio
import rp2
import machine
from machine import Pin

GP_IN_PIN = 0
STATE_MACHINE_ID = 0
counter = 0
instance_sm0 = None

irq_flag = asyncio.ThreadSafeFlag()
irq_sm_instance = None



#
# IRQ handler for PIO state machine.
# Stores the triggering SM instance and sets the thread-safe flag.
# Kept minimal ? no print(), no heap allocation.
#
def pio_irq_handler(intr_sm):
    global irq_sm_instance
    irq_sm_instance = intr_sm
    irq_flag.set()



#
# Asyncio task that waits for the IRQ flag and processes the event
# in the main context, where print() and counter update are safe.
#
async def pio_irq_task():
    global counter
    global irq_sm_instance
    while True:
        await irq_flag.wait()   # wait until irq set
        print('IRQ from SM:', irq_sm_instance)
        if irq_sm_instance == instance_sm0:
            print('--------------------')
            print('IRQ_SM0 is set')
            counter += 1
            print(f'counter: {counter}')
            irq_sm_instance = None
        else:
            print('IRQ_SM0 is not set')    


@rp2.asm_pio()            
def sw_w_wait_irq():
    # wrap_target()    # may skip
    wait(0,pin,0)      # wait until GPIO 0 becomes LOW
    irq(0)             # set IRQ flag
    wait(1,pin,0)      # wait until GPIO 0 becomes HIGH
    # wrap()           # may skip

async def main():

    global instance_sm0
    # to enable 2KHz to StateMachine, set systemclock to 125MHz
    machine.freq(125_000_000)
    sw_pin = Pin(GP_IN_PIN, mode=Pin.IN, pull=Pin.PULL_UP)
    instance_sm0 = rp2.StateMachine(STATE_MACHINE_ID, sw_w_wait_irq, freq=2000, in_base=sw_pin)
    instance_sm0.irq(handler=pio_irq_handler)
    asyncio.create_task(pio_irq_task())

    print('start Statemachine')
    instance_sm0.active(1)
    await asyncio.sleep(10)
    instance_sm0.active(0)
    print('stopped Statemachine')


asyncio.run(main())
print('end of async task, bye')


#
#
#