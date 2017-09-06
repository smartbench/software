# example using pyserial
# sudo pip3 install pyserial
# intro:
# https://pythonhosted.org/pyserial/shortintro.html
# https://pythonhosted.org/pyserial/pyserial_api.html

import serial
ftdi = serial.Serial('/dev/ttyUSB1', baudrate=921600, timeout=2)
ftdi.is_open

N1 = 100
N2 = 100000
#trama = bytes([1,2,3])

data_wr = range(N1)
data_rd = []
data = []

for i in range(N2):
    data_rd = []
    data = []
    trama = bytes(i % 256 for i in range(i, i+N1))
    ftdi.write(trama)
    while(len(list(data)) < len(list(trama))):
        data_rd = list(ftdi.read(N1))
        data = data + data_rd
    #print( "({})\tin_waiting={}\tout_waiting={}\tdata_rd={}".format(i, ftdi.in_waiting, ftdi.out_waiting, data_rd) )
    #print( "Sent={}\tRead={}".format( list(trama) , list(data_rd) ) )
    if(0==(i%100)): print("\rN={}".format(i))
    if(list(trama) != list(data_rd)):
        print( "\rSent={}\tRead={}".format( list(trama) , list(data_rd) ) )
        break

ftdi.close()


# read
# readinto
# in_waiting
# out_waiting
