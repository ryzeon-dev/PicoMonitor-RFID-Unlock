import sys
import time
from lib import start, RFID
from machine import Pin, I2C, Timer, reset
from oled import SSD1306_I2C
import debian
from font import printString as write

global waiting, status, started
waiting = [None, None, None, None, None, None, None, None, None, None]
status = None
started = False

def callback():
    global waiting, status, started
    
    if not started:
        return
    
    sleeping = False not in waiting and None not in waiting

    if sleeping:
        print(waiting)
        waiting = [None for i in range(20)]
        machine.soft_reset()
    else:
        if status is not None:
            waiting.pop(0)
            waiting.append(not status)

Timer(period=1800, mode=Timer.PERIODIC, callback=lambda t:[ callback() ])

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
    status = False

    recv = sys.stdin.readline().strip()
    recv = recv.split(':')
    started = True
    status = True
    
    oled1.fill(0)
    oled1.text('RasPico Monitor', 0, 0)
    oled1.text(f'CPU: {recv[0]}% - {recv[1]} C', 0, 16)
    oled1.text(f'RAM: {recv[2]}%', 0, 26)
    oled1.text(f'  CACHE: {recv[3]}', 0, 36)
    oled1.text(f'SWAP: {recv[4]}%', 0, 46)
    oled1.text(f'  CACHE: {recv[5]}', 0, 56)
    oled1.show()
    
    oled2.fill(0)
    oled2.text('RasPico Monitor', 0, 0)
    oled2.text(f'LOAD: {recv[6]}', 0, 16)
    oled2.text(f'UPLD: {recv[7]}', 0, 26)
    oled2.text(f'DWLD: {recv[8]}', 0, 36)
    oled2.text(f'RDNG: {recv[9]}', 0, 46)
    oled2.text(f'WRTN: {recv[10]}', 0, 56)
    oled2.show()
    
    content = rfid.readContent()

    if content:
        if content == 'CHANGE THIS TEXT WITH YOUR OWN SECURITY PHRASE':
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