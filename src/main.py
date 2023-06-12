import sys
import time
from lib import start, RFID
from machine import Pin, I2C
from oled import SSD1306_I2C
import debian
from font import printString as write

start()

i2c1 = I2C(0, sda=Pin(16), scl=Pin(17))
i2c2 = I2C(1, sda=Pin(26), scl=Pin(27))

oled1 = SSD1306_I2C(128, 64, i2c2)
oled1.fill(0)
debian.draw(oled1)
oled1.show

oled2 = SSD1306_I2C(128, 64, i2c1)
oled2.fill(0)
debian.draw(oled2)
oled2.show()

rfid = RFID(sda=1, sck=2, mosi=3, miso=4)

while True:
    recv = sys.stdin.readline().strip()
    recv = recv.split(':')
    
    oled1.fill(0)
    oled1.text('RasPico Monitor', 0, 0)
    write(oled1, f'CPU: {recv[0]}%', 0, 16)
    write(oled1, f'RAM: {recv[1]}', 0, 32)
    write(oled1, f'LD: {" " + recv[2] if len(recv[2]) <= 3 else recv[2]}', 0, 48)
    oled1.show()
    
    oled2.fill(0)
    oled2.text('RasPico Monitor', 0, 0)
    write(oled2, f'TMP:{" " + recv[3] if len(recv[3]) <= 3 else recv[3]}C', 0, 16)
    write(oled2, f'UPL:{" " + recv[4] if len(recv[4]) <= 3 else recv[4]}', 0, 32)
    write(oled2, f'DWL:{" " + recv[5] if len(recv[5]) <= 3 else recv[5]}', 0, 48)
    oled2.show()
    
    content = rfid.readContent()

    if content:
        if content == 'CONTENT OF YOUR TOKEN':
            oled2.fill(0)
            oled2.text('RasPico Monitor', 0, 0)
            oled2.text('ACCESS', 0, 20)
            oled2.text('UTHORIZED', 0, 40)
            oled2.show()
            print('access granted')
        else:
            oled2.fill(0)
            oled2.text('RasPico Monitor', 0, 0)
            oled2.text('ACCESS', 0, 20)
            oled2.text('DENIED', 0, 40)
            oled2.show()
            print('null')
    else:
        print('null')
