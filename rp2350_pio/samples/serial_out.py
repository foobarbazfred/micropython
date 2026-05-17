#
# https://micropython-docs-ja.readthedocs.io/ja/latest/rp2/quickref.html#programmable-io-pio
#

#
# asm_pio .... assemble and make code of PIO program
#

STATE_MACHINE_ID = 0
LED_PIN = 1

from machine import Pin
import rp2

#
# must set shiftdir
@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def blink():
    pull()       # TX FIFO -> OSR
    set(x, 7)
    label('loop')
    out(pins, 1)  # OSR -> GPIO with 1bit shift (shift left)
    jmp(x_dec, 'loop')  # if x is not 0 then x-- and jump else next line


machine.freq(96_000_000)
LOW_FREQ = int(96_000_000 / 0xFFF8)

led_pin = Pin(LED_PIN, Pin.OUT)

# create Statemachine_0 that uses Pin(1) and code is blink
sm0 = rp2.StateMachine(STATE_MACHINE_ID, blink, freq=LOW_FREQ , out_base=led_pin)

# start StateMachine
sm0.active(1)

while True:
    sm0.put(0xE5)
    sm0.put(0xA5)
    time.sleep(1)


# stop StateMachine
sm0.active(0)
