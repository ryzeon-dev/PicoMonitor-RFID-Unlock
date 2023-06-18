# PicoMonitor-RFID-Unlock
Raspberry Pi Pico based stats monitor &amp; RFID unlock

![Sample](https://github.com/cpy-dev/PicoMonitor-RFID-Unlock/blob/main/sample.png)

# Hardware
![Scheme](https://github.com/cpy-dev/PicoMonitor-RFID-Unlock/blob/main/scheme.png)

- Raspberry Pi Pico
- MFRC522 RFID module 
- 2x Oled module SSD1306 128x64 I2C
- push button

# Firmware
For this projects I used [MicroPython](https://micropython.org/download/rp2-pico/), it is suggested to do so if you wish to use my code.

# Software
Code is available in the src directory, all you need to do is to copy the files into you Pico and run it. \
The RFID-MFRC522 is handled using [this library](https://github.com/cpy-dev/RFID-micropython-mfrc522)

# Host code
The code has been tested and used in GNU/Linux, and partially on MacOs. You might need to adapt it in order to use it in other operating systems