#
#  IRQ test  for interrupt handler
#  SM_11  (PIO_2, SM_3)
#
import time
import micropython
import machine
import rp2

STATE_MACHINE_ID = 11  # 
sm = None

def pio_intr_handler(intr_sm):
    micropython.schedule(pio_handler_scheduled, intr_sm)

def pio_handler_scheduled(intr_sm):
    print('IRQ from SM:', intr_sm)
    if intr_sm == sm:
        print('--------------------')
        print('IRQ from SM 11')
    else:
        print('not from SM 11')    

@rp2.asm_pio()            
def only_irq():
    irq(rel(0))        

def main():
    global sm

    # to enable 2KHz to StateMachine, set systemclock to 125MHz
    machine.freq(125_000_000)
    sm = rp2.StateMachine(STATE_MACHINE_ID, only_irq, freq=2000)
    sm.irq(handler=pio_intr_handler)
    print('start sm_x')
    sm.active(1)
    time.sleep(10)
    sm.active(0)
    print('stop sm_x')

main()


