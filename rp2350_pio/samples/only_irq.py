import time
import micropython
import machine
import rp2

STATE_MACHINE_ID = 0
sm_0 = None


def pio_intr_handler(intr_sm):
    micropython.schedule(pio_handler_scheduled, intr_sm)

def pio_handler_scheduled(intr_sm):
    print('IRQ from SM:', intr_sm)
    if intr_sm == sm_0:
        print('--------------------')
        print('IRQ from SM_0')
    else:
        print('not from SM_0')    

@rp2.asm_pio()            
def only_irq():
    irq(0)        # set IRQ(0) flag  

def main():
    global sm_0

    # to enable 2KHz to StateMachine, set systemclock to 125MHz
    machine.freq(125_000_000)
    sm_0 = rp2.StateMachine(STATE_MACHINE_ID, only_irq, freq=2000)
    sm_0.irq(handler=pio_intr_handler)
    print('start sm_0')
    sm_0.active(1)
    time.sleep(10)
    sm_0.active(0)
    print('stop sm_0')

main()



#
#
#
