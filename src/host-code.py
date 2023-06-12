# THIS CODE IS TESTED AND USED ONLY IN LINUX
# IT MIGHT BE REQUIRED TO ADAPT IT IN ORDER 
# TO USE IT IN OTHER OPERATING SYSTEMS

from subprocess import getoutput
from time import time, sleep
from _thread import start_new_thread

import psutil
import serial
import threading
import sys
import os

class Monitor:
    def __init__(self, port=None):
        self.serial = None
        self.active = False
        self.warning = False
        self.port = port
        self.main()

    def main(self):
        while True:
            if self.active:
                sleep(1)
                continue

            while self.serial is None:
                print(f'[*] Serial port not identified')
                self.makeSerialConnection()
                sleep(1)

            self.mainThread = threading.Thread(target=self.communication, args=())
            self.mainThread.start()

    def makeSerialConnection(self):
        if self.port:
            self.serial = serial.Serial(self.port, baudrate=115200)
        else:
            port = getoutput('ls -l /dev/serial/by-id | grep MicroPython | awk -F \'../../\' \'{print $2}\'')
            if port:
                print(f'[*] Serial port identified: /dev/{port}')
                self.port = port
                self.serial = serial.Serial('/dev/' + port, baudrate=115200)
                
    def communication(self):
        self.mainThreadStopper = threading.Event()
        self.active = True

        bytesSent = psutil.net_io_counters().bytes_sent
        bytesRecv = psutil.net_io_counters().bytes_recv
        last = time()

        while True:
            cpu = psutil.cpu_percent()
            ram = getoutput('echo $(cat /proc/meminfo | grep MemTotal | awk \'{ print $2 }\' && cat /proc/meminfo |'
                                ' grep MemAvailable | awk \'{ print $2 }\') | awk \'{ printf \"%d %s (%.2f GB)\", ($1 - $2) *'
                                ' 100 / $1, "%", ($1 -$2) / 1024 / 1024 }\'')
            load = getoutput('uptime | awk -F \'load average: \' \'{ print $2 }\' | awk -F \', \' \'{ print $1 }\'')

            temp = psutil.sensors_temperatures()['coretemp'][0].current

            now = time()

            sent = psutil.net_io_counters().bytes_sent
            recv = psutil.net_io_counters().bytes_recv

            upload = (sent-bytesSent) / (now-last)
            uploadUnit = 'B'

            while upload > 1024:
                upload /= 1024
                if uploadUnit == 'B':
                    uploadUnit = 'K'
                elif uploadUnit == 'K':
                    uploadUnit = 'M'
                elif uploadUnit == 'M':
                    uploadUnit = 'G'
                else:
                    break

            download = (recv-bytesRecv) / (now-last)
            downloadUnit = 'B'

            while download > 1024:
                download /= 1024
                if downloadUnit == 'B':
                    downloadUnit = 'K'
                elif downloadUnit == 'K':
                    downloadUnit = 'M'
                elif downloadUnit == 'M':
                    downloadUnit = 'G'
                else:
                    break

            bytesSent = sent
            bytesRecv = recv
            last = now
            
            text = f'{round(cpu)}:{ram}:{load}:{round(temp)}:{round(upload)}{uploadUnit}:{round(download)}{downloadUnit}\n'
            print(f'[*] Sending: {text.strip()}')
            
            try:    
                self.serial.write(text.encode())
                self.waiting = randint(1, 1000)
                recv = self.serial.readline().decode().strip()
            except:
                self.waiting = 0
                self.serial = None
                break
            else:
                self.waiting = 0

            print(f'[*] Serial recv: {recv}')

            if recv == 'access granted':
                print('[*] Unlock request received')
                state = getoutput('dbus-send --session --dest=org.freedesktop.ScreenSaver --type=method_call --print-reply /org/freedesktop/ScreenSaver org.freedesktop.ScreenSaver.GetActive | grep boolean | awk \'{ print $2 }\'')

                if state == 'true':
                    for i in range(7):

                        try:
                            os.system(f'loginctl unlock-session {i}')
                        except: pass

            sleep(0.1)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        Monitor(sys.argv[1])
    else:
        Monitor()
