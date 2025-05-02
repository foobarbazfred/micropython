
from machine import ADC
from machine import Pin

# for setup LCD
from machine import I2C
from st7032 import ST7032LCD

# from gp2y0a21yk import GP2Y0A21YK


def main():
    # setup LCD
    i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=10_000) # OK??
    lcd =  ST7032LCD(i2c)
  
    # setup distance sensor
    adc = ADC(Pin(26))     
    gp2y = GP2Y0A21YK(adc)

    while True:
        dist, vol = gp2y.measure_distance()
        if dist is None:
           dist = -1
        report = f'dist: {dist:4.2f} cm\nvol: {vol:4.2f} V'
        print('----------------------------------')
        print(report)
        lcd.print(report, cls = True)

main()
    
