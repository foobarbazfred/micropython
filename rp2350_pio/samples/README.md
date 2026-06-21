# RP2350 PIO Samples

This directory contains sample programs using Programmable I/O (PIO) on the Raspberry Pi Pico 2 (RP2350).

## Sample List

### LED Blink Samples

#### 1. **blink_w_set.py**
A simple sample that directly controls GPIO pins using PIO's `set` instruction to blink an LED.
- **Features**: Simplest implementation
- **Use Case**: Learn the basics of PIO
- **Key Instructions**: `set(pins, 0/1)`

#### 2. **blink_by_sideset.py**
A sample that uses the `sideset` feature to blink an LED. GPIO is controlled as a side effect of instructions.
- **Features**: GPIO control via sideset
- **Use Case**: Control GPIO in parallel with complex operations
- **Key Instructions**: `.side(0/1)` modifier

#### 3. **blink_w_out.py**
A sample that reads values from TX FIFO and uses the `out` instruction to control an LED. Shift direction is right shift.
- **Features**: Right shift output from FIFO data
- **Use Case**: Dynamically send data from Python to control LED
- **Key Instructions**: `pull()`, `out(pins, 1)`
- **Python Side**: Send values with `sm.put(1)` / `sm.put(0)`

#### 4. **blink_w_out_shiftleft.py**
Similar to `blink_w_out.py` but uses left shift. Data is output starting from MSB (Most Significant Bit).
- **Features**: Left shift output from FIFO data
- **Use Case**: When output must start from MSB
- **Key Instructions**: `pull()`, `out(pins, 1)` with `SHIFT_LEFT`
- **Python Side**: Send MSB-set values (e.g., `0x8000_0000`)

#### 5. **blink_by_set_w_wait_loop.py**
A sample that controls LED blink speed using a wait loop with `set` and `jmp` instructions.
- **Features**: Delay control using PIO internal registers
- **Use Case**: Implement delays on hardware side
- **Key Instructions**: `set(pins, 0/1)`, `mov(x,y)`, `jmp(x_dec, label)`
- **Python Side**: Set delay count value to scratch register `Y`

### Input Samples

#### 6. **sw_w_in.py**
A sample that reads switch (button) state. GPIO bits are read into ISR using `in` instruction and sent to RX FIFO with `push`.
- **Features**: GPIO input reading
- **Use Case**: Monitor switch or sensor state
- **Key Instructions**: `in_(pins, 1)`, `push()`
- **Python Side**: Read values from FIFO with `sm.get()`

### IRQ (Interrupt) Samples

#### 7. **only_irq.py**
A simple sample that triggers PIO IRQ. State Machine 0 sets an IRQ flag, which is processed in Python's main context.
- **Features**: Basic IRQ usage
- **Use Case**: IRQ notification from PIO
- **Key Instructions**: `irq(0)`
- **Python Side**: Set handler with `sm.irq(handler=...)`

#### 8. **only_irq_sm11.py**
A sample that triggers IRQ on State Machine 11 (in PIO_2). Similar to `only_irq.py` but uses a different SM.
- **Features**: IRQ processing across multiple PIO blocks
- **Use Case**: Verify IRQ processing with higher State Machine IDs
- **Key Instructions**: `irq(rel(0))`

#### 9. **sw_w_wait_irq.py**
A sample that waits for switch input and generates an IRQ after confirmation. Simple implementation.
- **Features**: GPIO change detection and IRQ generation
- **Use Case**: Button input notification
- **Key Instructions**: `wait(0, pin, 0)`, `irq(0)`, `wait(1, pin, 0)`
- **Python Side**: Execute handler in main context with `micropython.schedule()`

#### 10. **sw_w_wait_debounce_irq.py**
A sample that adds debounce processing to switch input. Uses a PIO `jmp` loop to implement 30ms delay, removing noise before generating IRQ.
- **Features**: Hardware debounce + IRQ notification
- **Use Case**: Reliable physical switch input processing
- **Key Instructions**: `wait(0, pin, 0)`, `set(x, 29)`, `jmp(x_dec, label)`, `irq(0)`
- **Debounce Calculation**: 2KHz SM × 30 loops = 30ms

#### 11. **sw_w_wait_irq_async.py**
A sample that implements IRQ processing with Asyncio. Uses `asyncio.ThreadSafeFlag` for safe communication between IRQ handler and async task.
- **Features**: Asyncio integration, memory-efficient IRQ handler
- **Use Case**: Asynchronous event-driven programming
- **Key Instructions**: `wait(0, pin, 0)`, `irq(0)`
- **Python Side**: `asyncio.ThreadSafeFlag`, `await irq_flag.wait()`

### State Machine Synchronization Samples

#### 12. **sync_sm_by_irq.py**
A sample that synchronizes two State Machines (SM0 and SM1) via IRQ. SM0 generates IRQ(5), and SM1 waits for it, then generates its own IRQ(1).
- **Features**: Handshaking between State Machines
- **Use Case**: Coordinate multiple SMs
- **Key Instructions**: `irq(block, 5)`, `wait(1, irq, 5)`, `irq(clear, 5)`

#### 13. **test_pio_cross_irq.py**
A sample that performs IRQ synchronization across different PIO blocks. Sends IRQ from SM0 in PIO_1 to SM1 in PIO_0, testing cross-PIO communication.
- **Features**: IRQ communication across PIO blocks
- **Use Case**: Complex systems using multiple PIO blocks
- **Key Instructions**: `irq(block, 5)`, `wait(1, irq, 5)`, `sm.exec()` for machine code execution
- **Note**: `sm4.exec(0xc00d)` is the machine code representation of IRQ(5)

### Serial Output Samples

#### 14. **serial_out.py**
A sample that outputs 8-bit serial data. Reads one byte from FIFO and outputs it bit-by-bit via GPIO.
- **Features**: Basic serial communication implementation
- **Use Case**: Bit-serial output to external devices
- **Key Instructions**: `pull()`, `set(x, 7)`, `out(pins, 1)`, `jmp(x_dec, label)`
- **Data Format**: 8 bits (output 8 times in loop)

#### 15. **serial_out_slow.py**
Similar to `serial_out.py` but adds delays using `nop() [31]` instruction to significantly reduce output speed.
- **Features**: Low-speed serial output
- **Use Case**: Support for low-speed devices
- **Key Instructions**: `nop() [31]` (31-clock delay)
- **Delay**: Adds approximately 16ms delay between each bit output

## PIO Programming Basics

### Commonly Used Instructions
- **`set(pins, value)`**: Set value directly to pins
- **`out(pins, n)`**: Output top n bits of OSR (Output Shift Register) to pins
- **`in_(pins, n)`**: Read n bits from pins into ISR (Input Shift Register)
- **`pull()`**: Transfer data from TX FIFO to OSR
- **`push()`**: Transfer data from ISR to RX FIFO
- **`irq(flag)`**: Set IRQ flag
- **`wait(level, source, index)`**: Wait until condition is met
- **`jmp(condition, label)`**: Conditional jump

### State Machine Configuration Parameters
- **`freq`**: State Machine clock frequency (Hz)
- **`set_base`**: Pin base used by `set` instruction
- **`out_base`**: Pin base used by `out` instruction
- **`in_base`**: Pin base used by `in_` instruction
- **`sideset_base`**: Pin base used by `sideset` feature

## How to Run

```python
import rp2
from machine import Pin

# Define PIO assembly function
@rp2.asm_pio()
def my_program():
    set(pins, 0)
    set(pins, 1)

# Create State Machine
sm = rp2.StateMachine(0, my_program, freq=2000, set_base=Pin(1))

# Run
sm.active(1)  # Start
# ... processing ...
sm.active(0)  # Stop
```

## References
- [MicroPython RPi Pico Quick Reference](https://docs.micropython.org/en/latest/rp2/quickref.html#programmable-io-pio)
- RP2040/RP2350 Datasheet
