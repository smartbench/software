# example using pyserial
# sudo pip3 install pyserial
# intro:
# https://pythonhosted.org/pyserial/shortintro.html

import serial
ftdi = serial.Serial('/dev/ttyUSB1', baudrate=921600, timeout=2)
#ftdi.baudrate = 921600
ftdi.is_open
ftdi.write(bytes([3]))
data = ftdi.read(5)
list(data)

ftdi.close()
