# example using pyserial
# sudo pip3 install pyserial
# intro:
# https://pythonhosted.org/pyserial/shortintro.html
# https://pythonhosted.org/pyserial/pyserial_api.html

import serial
import time


ftdi = serial.Serial('/dev/ttyUSB1', baudrate=921600, timeout=2)
ftdi.is_open

N1 = 10000
N2 = 100000
#trama = bytes([1,2,3])

data_wr = range(N1)
data_rd = []
data = []
j=0
k=0
c1 = 0

t1 = time.time()
for i in range(N2):
    data_rd = []
    data = []
    t1 = time.time()
    trama = bytes(i % 256 for i in range(i, i+N1))
    ftdi.write(trama)
    while(len(list(data)) < len(list(trama))):
        data_rd = list(ftdi.read(N1-len(data)))
        data = data + data_rd
    k=k+1
    j=j+N1
    c1=c1+N1
    #print( "({})\tin_waiting={}\tout_waiting={}\tdata_rd={}".format(i, ftdi.in_waiting, ftdi.out_waiting, data_rd) )
    #print( "Sent={}\tRead={}".format( list(trama) , list(data_rd) ) )
    if(0==(k%100)):
        t2 = time.time()
        #t2 = time.time()
        vel = c1 / (t2-t1)
        c1 = 0

        print("\rN={}\tSPEED={} MBPS".format(j, vel/1.0e6))
    if(list(trama) != list(data_rd)):
        print( "\rSent={}\tRead={}".format( list(trama) , list(data_rd) ) )
        break

ftdi.close()


# read
# readinto
# in_waiting
# out_waiting
