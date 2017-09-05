# example using pyserial
# sudo pip3 install pyserial
# intro:
# https://pythonhosted.org/pyserial/shortintro.html
# https://pythonhosted.org/pyserial/pyserial_api.html

import serial
import sys
import time
from statistics import mean


ftdi = serial.Serial('/dev/ttyUSB1', baudrate=115200, timeout=2)
ftdi.is_open

N1 = 1000
N2 = 100000
#trama = bytes([1,2,3])

data_wr = range(N1)
data_rd = []
data = []
errors = 0
enviados = 0
recibidos = 0

N= 30

print("""Units:
  Enviados: Bytes
  Recibidos: Bytes
  Errors: Bytes
  Bps: Bytes por segundo
""")
while True:
    t = []
    trama = bytes([i%256 for i in range(10000) ])
    for _ in range(N):
        t1 = time.time()
        enviados = enviados + ftdi.write(trama)
        data_rd = ftdi.read(len(trama))
        t2 = time.time()
        t.append(t2-t1)
        if trama != bytes(data_rd):
            for n,c in enumerate(trama):
                 if data_rd[n] != c:
                        errors = errors + 1
        recibidos = recibidos + len(data_rd)

    t_mean = mean(t)
    sys.stdout.write( "\r Enviados: {} Recibidos: {}  Errors: {} ({:.2}%)  Bps: {:.2}".format(enviados, recibidos, errors,errors/recibidos , len(trama)*2/(t_mean ) ))

ftdi.close()


# read
# readinto
# in_waiting
# out_waiting
