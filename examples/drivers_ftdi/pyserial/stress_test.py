# example using pyserial
# sudo pip3 install pyserial
# intro:
# https://pythonhosted.org/pyserial/shortintro.html
# https://pythonhosted.org/pyserial/pyserial_api.html

import serial
import sys
import time
from statistics import mean

ftdi = serial.Serial('/dev/ttyUSB1', baudrate=921600, timeout=2)
ftdi.is_open

N1 = 10000
N2 = 100000
#trama = bytes([1,2,3])

data_wr = range(N1)
data_rd = []
data = []

print("""Units:
  Enviados: Bytes
  Recibidos: Bytes
  errores: Bytes
  Bps: Bytes por segundo
""")

TIMEOUT = 3.0
t = []
enviados = 0
recibidos = 0
errores = 0
t1 = time.time()

for i in range(N2):
    data_rd = []
    data = []
    trama = bytes(i % 256 for i in range(i, i+N1))
    ftdi.write(trama)
    while(len(list(data)) < N1):
        data_rd = list(ftdi.read(N1-len(data)))
        data = data + data_rd
        if(time.time()-t1 > TIMEOUT): break
    recibidos=recibidos+len(data)
    #print( "({})\tin_waiting={}\tout_waiting={}\tdata_rd={}".format(i, ftdi.in_waiting, ftdi.out_waiting, data_rd) )
    #print( "Sent={}\tRead={}".format( list(trama) , list(data_rd) ) )
    t2 = time.time()
    t.append(t2-t1)
    vel = len(data) / (t2-t1)
    t1 = t2
    t_mean = mean(t)
    #print("\rN={}\tSPEED={} MBPS".format(j, vel/1.0e6))

    if trama != bytes(data):
        for n,c in enumerate(list(trama)):
             if data[n] != c:
                    errores = errores + 1

    sys.stdout.write( \
        "\r Enviados: {} Recibidos: {}  Errores: {} ({:.2}%)  Bps: {:.2}".format( \
         enviados, recibidos, errores, 100*errores/recibidos , (len(data)+len(trama)) / t_mean ) )

    # if(list(trama) != list(data_rd)):
    #     print( "\rERROR!\tSent={}\tRead={}".format( list(trama) , list(data_rd) ) )
    #     break

ftdi.close()


# read
# readinto
# in_waiting
# out_waiting
