#
# PIO Sample: Switch Input with Debounce and IRQ Notification
#
# Overview:
#   Reads a momentary push switch via PIO state machine.
#   Debounce is handled entirely in PIO (no software polling required).
#   On a confirmed press, the state machine fires an IRQ to notify MicroPython.
#
# Features:
#   - Hardware debounce via PIO loop (30 ms wait)
#   - IRQ-driven notification to MicroPython main context via asyncio.ThreadSafeFlag
#   - No busy-waiting in MicroPython; event is processed in main context by schedule
#
# Target:
#   Raspberry Pi Pico 2 (RP2350) / MicroPython
#

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


#
# w/ debounce function
#
# Debounce timing calculation:
#   SM clock      : 2000 Hz  ->  500 us per instruction
#   Target wait   : 30 ms
#   Required cycles: 30 ms / 500 us = 60 cycles
#   jmp [1] costs 2 cycles per iteration (1 + 1 delay)
#   Number of loops: 60 / 2 = 30
#   set(x, 29) gives 30 iterations (counts down from 29 to 0, inclusive)
#
@rp2.asm_pio()
def sw_w_wait_irq():
    label('top')
    # wrap_target()    # may skip
    wait(0, pin, 0)    # wait until pin goes LOW (button pressed)
    set(x, 29)         # loops 30 times (x=29 down to 0) 
    label('debounce_loop')
    jmp(x_dec, 'debounce_loop') [1]  # decrement X, loop until zero (2 cycles per iteration)
    jmp(pin, 'top')    # if pin is HIGH, treat as noise and restart
    irq(0)             # pin confirmed LOW after debounce, fire IRQ
    wait(1, pin, 0)    # wait until pin goes HIGH (button released)
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