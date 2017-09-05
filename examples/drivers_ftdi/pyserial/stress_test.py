# example using pyserial
# sudo pip3 install pyserial
# intro:
# https://pythonhosted.org/pyserial/shortintro.html
# https://pythonhosted.org/pyserial/pyserial_api.html

import serial
ftdi = serial.Serial('/dev/ttyUSB1', baudrate=921600, timeout=2)
ftdi.is_open

N1 = 1000
N2 = 100000
#trama = bytes([1,2,3])

data_wr = range(N1)
data_rd = []
data = []

for i in range(N2):
    trama = bytes([i % 256])
    ftdi.write(trama)
    data_rd = list(ftdi.read(1))
    data = data + data_rd
    print( "({})\tin_waiting={}\tout_waiting={}\tdata_rd={}".format(i, ftdi.in_waiting, ftdi.out_waiting, data_rd) )
    print( "Sent={}\tRead={}".format( list(trama) , list(data_rd) ) )
    if(list(trama) != list(data_rd)):
        break

ftdi.close()


# read
# readinto
# in_waiting
# out_waiting
