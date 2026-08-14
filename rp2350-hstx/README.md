# RP2350 HSTX DVI Signal Generation Demo

A demonstration of DVI signal generation using the RP2350's HSTX (High Speed TX) feature. This project implements monochrome display (black/white) with a frame buffer to achieve 640x480 dot resolution DVI output.

## Overview

### Supported Environment
- **MPU**: RP2350 (126MHz)
- **Board**: Raspberry Pi Pico 2
- **Firmware**: MicroPython v1.28.0 or later

### Key Features
- 640x480 resolution DVI output (VGA standard)
- Monochrome display (1 bit per pixel)
- Frame buffer-based rendering
- Efficient data transfer using multiple DMA channels
- Line counting control via PIO

## Hardware Connection

### GPIO Usage (GP12-GP19)

Connection with DVI Socket Board ([pico-dvi-sock](https://github.com/wren6991/pico-dvi-sock)):

| Bit | Pin | GPIO | Signal |
|-----|-----|------|--------|
| 0 | D0+ | GP12 | Blue |
| 1 | D0- | GP13 | Blue |
| 2 | CLK+ | GP14 | CLK |
| 3 | CLK- | GP15 | CLK |
| 4 | D2+ | GP16 | Red |
| 5 | D2- | GP17 | Red |
| 6 | D1+ | GP18 | Green |
| 7 | D1- | GP19 | Green |

## Directory Structure

```
rp2350-hstx/
├── README.md                    # This file
├── README-ja.md                 # Japanese version
├── src/
│   ├── dvi_vga_mono_demo.py          # Main demo program
│   └── mylib.py                 # Utility functions (register operations)
└── docs/
    └── ...
```

### dvi_vga_mono_demo.py

The main DVI signal generation demo program with the following features:

#### Clock Configuration
- System Clock: 126MHz
- HSTX Clock: 126MHz

#### DMA Channel Configuration
- **DMA0**: VSYNC signal transfer
- **DMA1**: HSYNC signal transfer (ring configuration)
- **DMA2**: TMDS command transfer (Encode 640pixel command)
- **DMA3**: Display data transfer
- **DMA10**: PIO FIFO notification
- **DMA11**: Retrieve DMA control parameters from PIO

#### PIO (Programmable I/O)
- 480 line counting
- DMA chain control

#### Frame Buffers
- VSYNC/HSYNC timing buffer
- Display data buffer (aligned)
- TMDS command buffer

## Timing Configuration

### Front Porch
- (BLANK×16 + HSYNC×96 + BLANK×48 + BLANK×640) × 10 lines

### VSYNC
- (VSYNC×16 + HSYNC×96 + VSYNC×48 + VSYNC×640) × 2 lines

### Back Porch
- (BLANK×16 + HSYNC×96 + BLANK×48 + BLANK×640) × 33 lines

### Display Area
- (BLANK×16 + HSYNC×96 + BLANK×48 + data×640) × 480 lines

## Usage

### 1. Install Dependencies

Ensure `mylib.py` is placed in the src directory. This file must contain the following functions:
- `write_reg()`
- `write_CLK_HSTX_CTRL()`
- `write_CLK_HSTX_DIV()`
- `write_HSTX_CTRL_CSR()`
- `write_HSTX_CTRL_BIT()`
- `write_HSTX_CTRL_EXPAND_TMDS()`
- `write_HSTX_CTRL_EXPAND_SHIFT()`

### 2. Run the Demo

```python
import sys
sys.path.append('/path/to/rp2350-hstx/src')

# Execute dvi_vga_mono_demo.py
exec(open('dvi_vga_mono_demo.py').read())
```

### 3. Connect Display

Connect a DVI-compatible display to the DVI Socket Board.

## Version History

### V0.04 (2026/08/14)
- Display frame buffer improvements (reduced zipper artifacts)
- DMA configuration optimization
  - DMA0: VSYNC transfer
  - DMA1: HSYNC transfer
  - DMA2: TMDS command transfer
  - DMA3: Display data transfer

### V0.03 (2026/08/13)
- Fixed aligned buffer function calculation bug

### V0.02 (2026/08/12)
- Fixed TMDS control parameter
  - N_OF_PIXELS = 32

### V0.01 (2026/08/12)
- Initial release
- Monochrome display support
- 5 DMA channels
- 1 PIO

## Customization

### Changing Display Pattern

Modify `PIXEL_TEST_PATTERN` in the `setup_vga_display()` function:

```python
PIXEL_TEST_PATTERN = 0b1111_0000_1100_1100_1010_1010_1111_1111
```

Each bit corresponds to one pixel (1=white, 0=black).

### Debugging

GPIO 0-3 are configured for debugging and can be monitored with an oscilloscope:
- GP0: DMA0 interrupt (VSYNC)
- GP1: DMA1 interrupt (HSYNC)
- GP2: DMA2 interrupt (TMDS Command)
- GP3: DMA3 interrupt (Display data)

## References

- [Raspberry Pi Pico 2 Technical Specification](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
- [RP2350 Datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)
- [pico-dvi-sock Project](https://github.com/wren6991/pico-dvi-sock)

## License

This code is part of the MicroPython project.

## Troubleshooting

### Display not showing signal
1. Verify DVI Socket Board connections
2. Check that GPIO 12-19 are correctly connected
3. Monitor debug signals on GP0-3 with an oscilloscope

### Screen flickering
- Check the execution time of DMA interrupt handlers
- Try adjusting the system clock frequency

## Support

Please report issues and bug reports in the GitHub Issues section.
