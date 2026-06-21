#
# synchronize state machines (sm0 -> sm1)  by IRQ(5)
#

import time
import micropython
import machine
import rp2

IRQ_H = 1
IRQ_FOR_SYNC = 5
IRQ_FOR_NOTIFY = 1

sm0 = None
sm1 = None


def pio_intr_handler(intr_sm):
    micropython.schedule(pio_handler_scheduled, intr_sm)

def pio_handler_scheduled(intr_sm):
    print('IRQ from SM:', intr_sm)
    if intr_sm == sm1:
        print('--------------------')
        print('IRQ from sm1')
    else:
        print('not from sm1')    

@rp2.asm_pio()            
def inst_raise_irq():
    irq(block, 5)           # 5: IRQ_FOR_SYNC

@rp2.asm_pio()            
def inst_receive_irq():
    wait(1, irq, 5)         # 1: LEVEL_H , 5: IRQ_FOR_SYNC
    irq(clear, 5)           # 5: IRQ_FOR_SYNC
    irq(1)                  # 1: IRQ_FOR_NOTIFY


def main():
    global sm0
    global sm1

    # to enable 2KHz to StateMachine, set systemclock to 125MHz
    machine.freq(125_000_000)
    sm0 = rp2.StateMachine(0, inst_raise_irq, freq=2000)
    sm1 = rp2.StateMachine(1, inst_receive_irq, freq=2000)

    #sm0.irq(handler=pio_intr_handler)
    #sm1.irq(handler=pio_intr_handler, trigger=rp2.PIO.IRQ_SM1)
    sm1.irq(handler=pio_intr_handler)

    print('start sm_0, sm_1')
    sm0.active(1)
    sm1.active(1)
    time.sleep(3)
    sm0.active(0)
    sm1.active(0)
    print('stop sm_0, sm_1')


    print('start only sm_1')
    sm1.active(1)
    for _ in range(5):
       print('exec irq(5)')   
       sm0.exec('irq(5)')
       time.sleep(1)
    sm1.active(0)
    print('stop sm_1')    
    print('bye')    

main()


#
#
#
