# Example using the original D2XX drivers (in C) from Python.
# TODO: wrapper
# The functions are declared in
#   libftd2xx-x86_64-1.4.6/release/examples/ftd2xx.h
# A useful example code can be seen in:
#   /home/ariel/Descargas/libftd2xx-x86_64-1.4.6/release/examples/loopback/main.c

# Useful links
# https://docs.python.org/3/library/ctypes.html
# https://docs.python.org/2/library/ctypes.html
# https://stackoverflow.com/questions/1942298/wrapping-a-c-library-in-python-c-cython-or-ctypes
# https://stackoverflow.com/questions/21483482/efficient-way-to-convert-string-to-ctypes-c-ubyte-array-in-python
# https://stackoverflow.com/questions/15377338/convert-ctype-byte-array-to-bytes
# https://stackoverflow.com/questions/28488080/python-convert-bytearray-to-numbers-in-list


from ctypes import *
d2xx = CDLL('libftd2xx.so')
ftHandle = c_void_p()
ftHandle2 = c_void_p()
ftStatus = d2xx.FT_Open(0,  byref(ftHandle))
ftStatus = d2xx.FT_Open(1,  byref(ftHandle2))
ftHandle.value
ftHandle2.value
d2xx.FT_SetBaudRate(ftHandle2.value, 921600)
d2xx.FT_SetDataCharacteristics(ftHandle.value, 8,0,0)
written = c_void_p()
buff = (c_ubyte * 4)(*[1,2,3,4])
size = len(buff)
buff_ =cast(buff, c_char_p).value
d2xx.FT_Write(ftHandle2.value, buff_, size, byref(written))
written.value

bytesReceived = c_void_p()
d2xx.FT_GetQueueStatus(ftHandle2.value, byref(bytesReceived))
bytesReceived.value

bytesRead = c_void_p()
readBuffer = c_void_p()
d2xx.FT_Read(ftHandle2.value, byref(readBuffer), bytesReceived.value, byref((bytesRead)))
bytesRead.value
bytearray(readBuffer)
bytes(bytearray(readBuffer))
list(bytearray(readBuffer))[0:bytesRead.value]




from ctypes import *
d2xx = CDLL('libftd2xx.so')
ftHandle = c_void_p()
ftStatus = d2xx.FT_Open(1,  byref(ftHandle))
d2xx.FT_SetBaudRate(ftHandle.value, 921600)
d2xx.FT_SetDataCharacteristics(ftHandle.value, 8,0,0)
written = c_void_p()
buff_ =cast((c_ubyte * 4)(*[1,2,3,4]), c_char_p).value
d2xx.FT_Write(ftHandle.value, buff_, len(buff), byref(written))

bytesReceived = c_void_p()
d2xx.FT_GetQueueStatus(ftHandle.value, byref(bytesReceived))

bytesRead = c_void_p()
readBuffer = c_void_p()
d2xx.FT_Read(ftHandle.value, byref(readBuffer), bytesReceived.value, byref((bytesRead)))

list(bytearray(readBuffer))[0:bytesRead.value]
