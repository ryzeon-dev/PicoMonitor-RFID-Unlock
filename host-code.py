#!/usr/bin/python3

from random import randint
from subprocess import getoutput
from time import time, sleep
from _thread import start_new_thread

import psutil
import requests
import serial
import threading
import sys
import os

class Monitor:
    def __init__(self, port=None):
        self.serial = None
        self.active = None
        self.port = port
        self.main()

    def main(self):
        while True:
        
            if self.active:
                sleep(4)
                continue

            while self.serial is None:

                print(f'[*] Serial port not identified')
                self.makeSerialConnection()
                sleep(1)

            self.mainThread = threading.Thread(target=self.communication, args=())
            self.mainThread.start()

    def makeSerialConnection(self):
        if self.port:
            self.serial = serial.Serial(self.port, baudrate=115200, timeout=2)

        else:
            try:
                port = getoutput('ls -l /dev/serial/by-id | grep MicroPython | awk -F \'../../\' \'{print $2}\'')
                
            except:
                sys.exit(0)

            else:
                if port:
                    print(f'[*] Serial port identified: /dev/{port}')

                    self.port = port
                    self.serial = serial.Serial('/dev/' + port, baudrate=115200, timeout=2)

    def communication(self):
        self.active = True

        bytesSent = psutil.net_io_counters().bytes_sent
        bytesRecv = psutil.net_io_counters().bytes_recv
        bytesWritten = psutil.disk_io_counters().write_bytes
        bytesRed = psutil.disk_io_counters().read_bytes
        last = time()

        while True:
            cpu = psutil.cpu_percent()
            
            ram = getoutput('echo $(cat /proc/meminfo | grep MemTotal | awk \'{ print $2 }\' && cat /proc/meminfo |'
                            ' grep MemAvailable | awk \'{ print $2 }\') | awk \'{ printf "%d", ($1 - $2) * 100 / $1}\'').strip()

            cached = getoutput('cat /proc/meminfo | grep -m 1 "Cached" | awk  \'{ printf "%d MB", $2 / 1024}\'').strip()

            swap = getoutput('echo $(cat /proc/meminfo | grep SwapTotal | awk \'{ print $2 }\' && cat /proc/meminfo | '
                             'grep SwapFree | awk \'{ print $2 }\') | awk \'{ printf "%d", $1 ? ($1 - $2) * 100 / $1 : 0 }\'').strip()
            
            swapCached = getoutput('cat /proc/meminfo | grep SwapCached | awk \'{ printf "%d MB", $2 / 1024 }\'').strip()

            load = getoutput('uptime  | awk -F \'load average: \' \'{ print $2 }\' | awk -F \', \' \'{ print $1 }\'').replace(',', '.').strip()

            temp = psutil.sensors_temperatures()['coretemp'][0].current

            now = time()

            sent = psutil.net_io_counters().bytes_sent
            recv = psutil.net_io_counters().bytes_recv
            written = psutil.disk_io_counters().write_bytes
            red = psutil.disk_io_counters().read_bytes
            delta = now - last

            upload = (sent - bytesSent) / delta
            uploadUnit = 'Bps'

            download = (recv - bytesRecv) / delta
            downloadUnit = 'Bps'

            write = (written - bytesWritten) / delta
            writeUnit = 'Bps'

            read = (red - bytesRed) / delta
            readUnit = 'Bps'

            bytesSent = sent
            bytesRecv = recv
            bytesWritten = written
            bytesRed = red
            last = now

            while upload > 1024:
                upload /= 1024
                if uploadUnit == 'Bps':
                    uploadUnit = 'KBps'
                elif uploadUnit == 'KBps':
                    uploadUnit = 'MBps'
                elif uploadUnit == 'MBps':
                    uploadUnit = 'GBps'
                else:
                    break

            while download > 1024:
                download /= 1024
                if downloadUnit == 'Bps':
                    downloadUnit = 'KBps'
                elif downloadUnit == 'KBps':
                    downloadUnit = 'MBps'
                elif downloadUnit == 'MBps':
                    downloadUnit = 'GBps'
                else:
                    break

            while write > 1024:
                write /= 1024
                if writeUnit == 'Bps':
                    writeUnit = 'KBps'
                elif writeUnit == 'KBps':
                    writeUnit = 'MBps'
                elif writeUnit == 'MBps':
                    writeUnit = 'GBps'
                else:
                    break

            while read > 1024:
                read /= 1024
                if readUnit == 'Bps':
                    readUnit = 'KBps'
                elif readUnit == 'KBps':
                    readUnit = 'MBps'
                elif readUnit == 'MBps':
                    readUnit = 'GBps'
                else:
                    break            
            
            text = f'{round(cpu)}:{round(temp)}:{ram}:{cached}:{swap}:{swapCached}:{load}:{round(upload)} {uploadUnit}:{round(download)} {downloadUnit}:{round(write)} {writeUnit}:{round(read)} {readUnit}\n'
            print(f'[*] Sending: {text.strip()}')

            recv = ''
            
            try:    
                self.serial.write(text.encode())
                self.waiting = True
                recv = self.serial.readline().decode().strip()
                print(recv)
            except:
                self.waiting = False
                self.serial = None
                break
            else:
                self.waiting = False

            print(f'[*] Serial recv: {recv}')
            
            if recv == 'access granted':
                print('[*] Unlock request received')

                for i in range(10):
                    try:
                        os.system(f'loginctl unlock-session {i}') # tested in GNU/Linux only
                    except: pass

            sleep(0.2)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        Monitor(sys.argv[1])
    else:
        Monitor()
