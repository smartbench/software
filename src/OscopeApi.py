#!/usr/bin/python3

#from pyftdi.ftdi import Ftdi
import serial
#import time
from threading import Timer
from math import log
from array import array
#from struct import *
import time

#######################################################
################## FTDI bridge driver #################
#######################################################

class _Oscope_ftdi( ):

    _BYTEORDER = 'little' # 'big' # 'big' / 'little'

    def __init__(self,**kwargs):
        self.ftdi = 0
        self.status = 'closed'
#        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if(self.ftdi.is_open()):
            self.close();
            print("Closed USB device")

    def open( self, device='/dev/ttyUSB1' ):
        try:
            self.ftdi = serial.Serial(device, baudrate=921600, timeout=2)
            if(self.ftdi.is_open):
                self.status = 'opened'
                print("Opened device!")
                return True
            else:
                self.status = 'closed'
                print ("Device not connected!")
                return False
        except:
            self.status = 'closed'
            print ("Device not connected!")
            return False


    def close(self):
        self.ftdi.close()
        print ("Device closed.")

    def send( self, addr, data ):
        aux = bytes( [ int(addr) , int(data%256) , int((data>>8)%256) ] )
        try:
            n = self.ftdi.write( aux )
            print("written {} bytes: {}".format(len(list(aux)), aux))
            i = 0
        except serial.SerialException:
            print("ERROR: Device not connected!")
            return -1
        except:
            print("Unknown Error when trying to Write")
            return -1

    def receive(self, size, blocking=True, timeout=0):
        data = []
        if(blocking==True):
            if(timeout==0):
                while(len(data) < size):
                    try:
                        data = data + list(self.ftdi.read(size - len(data)))
                    except serial.SerialException:
                        print("ERROR: Device not connected!")
                        return -1
                    except:
                        print("Unknown Error when trying to Read")
                        return -1
                    if(len(data)>0): pass # print ("data=", data)
                    else: print ("receiving...")
                    if(len(data) < size):   time.sleep(0.3)
                    #print ("a) data=", data)
            else:
                to = Timeout(timeout)
                while(len(data) < size and to.timeout == False):
                    try:
                        data = data + list(self.ftdi.read(size - len(data)))
                    except serial.SerialException:
                        print("ERROR: Device not connected!")
                        return -1
                    except:
                        print("Unknown Error when trying to Read")
                        return -1
                    if(len(data) < size and to.timeout == False):   time.sleep(0.05)
                    #print ("b) data=", data)
                del to
        else:
            try:
                data = data + list(self.ftdi.read(size - len(data)))
            except serial.SerialException:
                print("ERROR: Device not connected!")
                return -1
            except:
                print("Unknown Error when trying to Read")
                return -1
            #print ("c) data=", data)
        print (data)
        return data

    def empty_read_buffer(self):
        data = range(10)
        try:
            while (len(data) == 10): data = self.ftdi.read(10)
        except serial.SerialException:
            print("ERROR: Device not connected!")
            return -1
        except:
            print("Unknown Error when trying to Read")
            return -1

    def isOpen(self):
        try:
            return self.ftdi.is_open
        except:
            return False


class Timeout (Timer):
    timeout = False
    def __init__(self, time, *args, **kwargs): #time in seconds
        timeout = False
        super(Timer, self).__init__(time, self.myFunction, *args, **kwargs)

    def myFunction(self):
        timeout = True
        self.cancel()

#######################################################
################# LIBRARY DEFINITIONS #################
#######################################################

class _Definitions ( object ):
    ### REGISTERS ADDRESSES ###

    # CHB addresses not unused
    # always used _ADDR_XXX_CHA + _nchanel where _nchanel is 0 for channel A and 1 for channel B.

    _ADDR_REQUESTS = 0
    _ADDR_SETTINGS_CHA = 1
    _ADDR_SETTINGS_CHB = 2
    _ADDR_DAC_CHA = 3
    _ADDR_DAC_CHB = 4
    _ADDR_TRIGGER_SETTINGS = 5
    _ADDR_TRIGGER_VALUE = 6
    _ADDR_PRETRIGGER = 8
    _ADDR_NUM_SAMPLES = 7
    _ADDR_ADC_CLK_DIV_CHA_L = 9
    _ADDR_ADC_CLK_DIV_CHA_H = 10
    _ADDR_ADC_CLK_DIV_CHB_L = 11
    _ADDR_ADC_CLK_DIV_CHB_H = 12
    _ADDR_N_MOVING_AVERAGE_CHA = 13
    _ADDR_N_MOVING_AVERAGE_CHB = 14

    ### BIT FIELDS ###
    # DEFINES ARE THE INITIAL BIT NUMBER OF THIS FIELD

    # SETTINGS_CHA, SETTINGS_CHB
    _CONF_CH_ATT = 5
    _CONF_CH_GAIN = 2
    _CONF_CH_DC_COUPLING = 1
    _CONF_CH_ON = 0

    # TRIGGER CONF REG
    _TRIGGER_CONF_SOURCE_SEL = 1
    _TRIGGER_CONF_EDGE = 0

    # Requests handler
    _RQST_START_IDX = 0
    _RQST_STOP_IDX = 1
    _RQST_CHA_IDX = 2
    _RQST_CHB_IDX = 3
    _RQST_TRIG_IDX = 4
    _RQST_RST_IDX = 5

    # TRIGGER Status
    _BUFFER_FULL = 0
    _TRIGGERED   = 0

    ### WIDTH DEFINITIONS ###
    _ADC_WIDTH = 8
    _DAC_WIDTH = 10
    _ADDR_WIDTH = 8

    ### CONFIGURATION BITS values ###

    # EDGE_VALUES
    POSITIVE_EDGE = 0
    NEGATIVE_EDGE = 1

    # TRIGGER_SOURCE_VALUES
    TRIGGER_SOURCE_CHA = 1
    TRIGGER_SOURCE_CHB = 2
    TRIGGER_SOURCE_EXT = 3

    COUPLING_AC     = 1
    COUPLING_DC     = 0

    MODE_SINGLE  = 0
    MODE_NORMAL  = 1
    MODE_AUTO    = 2

    # Channel ON/OFF
    CHANNEL_ON      = 0x1
    CHANNEL_OFF     = 0x0

#######################################################
#################### CHANNEL CLASS ####################
#######################################################

class _Channel( _Definitions ):

    def __init__( self, channel_number, oscope):
        # _nchannel is:
        # 0 -> channel A
        # 1 -> channel B
        self._nchannel = channel_number
        # FPGAs register values.
        # Use methods to get/set actual values.
        self._requests = 0
        self._settings = 0xE1
        self._dac_value = 2 ** ( self._DAC_WIDTH - 1 )
        self._nprom = 0
        self._clk_divisor = 3
        self.oscope = oscope

    # channel settings
    def get_attenuator( self ):
        return ( self._settings >> self._CONF_CH_ATT ) & 0x7

    def set_attenuator( self, att ):
        if att<8 and att>=0:
            self._settings &= ~( 0x7 << self._CONF_CH_ATT )
            self._settings |= att << self._CONF_CH_ATT
        else:
            print( "Attenuation selector must be a number between 0 and 7" )

    def get_gain( self ):
        return ( self._settings >> _CONF_CH_GAIN ) & 0x7

    def set_gain( self, gain ):
        if gain<8 and gain>=0:
            self._settings &= ~( 0x7 << self._CONF_CH_GAIN )
            self._settings |= gain << self._CONF_CH_GAIN
        else:
            print( "Gain selector must be a number between 0 and 7" )

    def get_coupling( self ):
        return ( self._settings >> self._CONF_CH_DC_COUPLING ) & 0x1

    def set_coupling_dc( self ):
        self._settings |= 1 << self._CONF_CH_DC_COUPLING

    def set_coupling_ac( self ):
        self._settings &= ~( 1 << self._CONF_CH_DC_COUPLING )

    def get_ch_status( self ):
        return ( self._settings >> self._CONF_CH_ON ) & 0x1

    def set_ch_on( self ):
        self._settings |= 1 << self._CONF_CH_ON

    def set_ch_off( self ):
        self._settings &= ~(1 << self._CONF_CH_ON)

    def send_settings( self ):
        self.oscope.send( self._ADDR_SETTINGS_CHA + self._nchannel, self._settings )

    # Offset value
    def get_offset( self ):
        return self._dac_value - 2**( self._DAC_WIDTH-1 )

    def set_offset( self, val ):
        self._dac_value = val + 2**( self._DAC_WIDTH-1 )
        self.oscope.send( self._ADDR_DAC_CHA + self._nchannel, self._dac_value )

    # Documentation for nprom:
    # Prom  Fpga_value
    # 1     0
    # 2     1
    # 4     2
    # 8     3
    # ...
    def get_nprom( self ):
        return int(2 ** _nprom)

    def set_nprom( self, n ):
        self._nprom = int(log(n,2))
        self.oscope.send( self._ADDR_N_MOVING_AVERAGE_CHA + self._nchannel, self._nprom )

    def get_clk_divisor( self ):
        return self._clk_divisor+1

    def set_clk_divisor( self, div ):
        self._clk_divisor = div-1
        self.oscope.send( self._ADDR_ADC_CLK_DIV_CHA_L + self._nchannel, self._clk_divisor&0xFFFF )
        self.oscope.send( self._ADDR_ADC_CLK_DIV_CHA_H + self._nchannel, (self._clk_divisor>>16)&0xFFFF )

#######################################################
##################### OSCOPE CLASS ####################
#######################################################

class Smartbench( _Definitions ):

    def __init__( self , device='/dev/ttyUSB1'):

        self.oscope = _Oscope_ftdi()
        self.oscope_status = self.oscope.open(device)

        # initial configuration:
        # Trigger Source:       Channel A
        # Trigger edge:         positive
        # Trigger value:        128
        # Number of samples:    100
        # Pretrigger:           0
        # Trigger mode:         normal
        self._trigger_settings = ( self.TRIGGER_SOURCE_CHA << self._TRIGGER_CONF_SOURCE_SEL ) | ( self.POSITIVE_EDGE << self._TRIGGER_CONF_EDGE )
        self._triger_value = 2 ** ( self._ADC_WIDTH-1 )
        self._num_samples  = 100
        self._pretrigger   = 0
        self._trigger_mode = self.MODE_NORMAL

        # Channel register instance
        self.chA = _Channel(0, self.oscope)
        self.chB = _Channel(1, self.oscope)


    def get_oscope_status (self):
        return (self.oscope_status)

    def isOpen(self):
        return self.oscope.isOpen()

    def request_start( self ):
        self.oscope.send( self._ADDR_REQUESTS, 1 << self._RQST_START_IDX )

    def request_stop( self ):
        self.oscope.send( self._ADDR_REQUESTS, 1 << self._RQST_STOP_IDX )

    def request_chA( self ):
        self.oscope.send( self._ADDR_REQUESTS, 1 << self._RQST_CHA_IDX )

    def request_chB( self ):
        self.oscope.send( self._ADDR_REQUESTS, 1 << self._RQST_CHB_IDX )

    def request_trigger_status( self ):
        self.oscope.send( self._ADDR_REQUESTS, 1 << self._RQST_TRIG_IDX )

    def request_reset( self ):
        self.oscope.send( self._ADDR_REQUESTS, 1 << self._RQST_RST_IDX )

    def receive_trigger_status( self ):
        data = self.oscope.receive( 1, blocking=True )
        print("data len={}".format( len(data) ) )
        print ("data={}".format(data[0]))
        buffer_full = (data[0] >> self._BUFFER_FULL) & 0x01
        triggered = (data[0] >> self._TRIGGERED) & 0x01
        return [buffer_full, triggered]

    def receive_channel_data( self , n=0 ):
        if(n==0): n = self._num_samples
        return self.oscope.receive(n, blocking=True)

    def get_trigger_edge( self ):
        return ( self._trigger_settings >> self._TRIGGER_CONF_EDGE ) & 0x1

    def set_trigger_posedge( self ):
        self._trigger_settings &= ~( 1 << self._TRIGGER_CONF_EDGE )

    def set_trigger_negedge( self ):
        self._trigger_settings |= ( 1 << self._TRIGGER_CONF_EDGE )

    def get_trigger_source( self ):
        return ( self._trigger_settings >> self._TRIGGER_CONF_SOURCE_SEL ) & 0x3

    def set_trigger_source_cha( self ):
        self._trigger_settings &= 0x3 << self._TRIGGER_CONF_SOURCE_SEL
        self._trigger_settings |= self.TRIGGER_SOURCE_CHA << self._TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_chb( self ):
        self._trigger_settings &= 0x3 << self._TRIGGER_CONF_SOURCE_SEL
        self._trigger_settings |= self.TRIGGER_SOURCE_CHB << self._TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_ext( self ):
        self._trigger_settings &= 0x3 << self._TRIGGER_CONF_SOURCE_SEL
        self._trigger_settings |= self.TRIGGER_SOURCE_EXT << self._TRIGGER_CONF_SOURCE_SEL

    def send_trigger_settings( self ):
        self.oscope.send( self._ADDR_TRIGGER_SETTINGS, self._trigger_settings )
        print("Trigger settings set to {}".format(hex(self._trigger_settings) ) )

    def get_trigger_value( self ):
        return self._trigger_value# - 2**( self._ADC_WIDTH-1 )

    def set_trigger_value( self, val ):
        self._trigger_value = (1 << self._ADC_WIDTH-1 ) + val
        self.oscope.send( self._ADDR_TRIGGER_VALUE, self._trigger_value )
        print("Trigger value set to {}".format(self._trigger_value))

    def get_number_of_samples( self ):
        return self._num_samples

    def set_number_of_samples( self, N ):
        self._num_samples = N
        self.oscope.send( self._ADDR_NUM_SAMPLES, self._num_samples )
        print("Num_samples set to {}".format(self._num_samples))

    def get_pretrigger( self ):
        return self._pretrigger

    def set_pretrigger( self, pt_value ):
        self._pretrigger = pt_value
        self.oscope.send( self._ADDR_PRETRIGGER, self._pretrigger )
        print("Pretrigger set to {}".format(self._pretrigger))

    def set_trigger_mode( self, mode ):
        self._trigger_mode = mode

    def set_trigger_mode_single ( self ): self.set_trigger_mode(self.MODE_SINGLE)
    def set_trigger_mode_normal ( self ): self.set_trigger_mode(self.MODE_NORMAL)
    def set_trigger_mode_auto   ( self ): self.set_trigger_mode(self.MODE_AUTO)

    def get_trigger_mode( self ):
        return self._trigger_mode

    def is_trigger_mode_single (self): return (self._trigger_mode == self.MODE_SINGLE)
    def is_trigger_mode_normal (self): return (self._trigger_mode == self.MODE_NORMAL)
    def is_trigger_mode_auto   (self): return (self._trigger_mode == self.MODE_AUTO)

    def get_chA_status(self): return self.chA.get_ch_status()
    def get_chB_status(self): return self.chB.get_ch_status()

    def setDefaultConfiguration(self):
        self.set_trigger_source_cha()
        self.set_trigger_negedge()
        self.set_trigger_value(-28)
        self.set_number_of_samples(150)
        self.set_pretrigger(50)
        self.send_trigger_settings()

        self.chA.set_attenuator(1)
        self.chA.set_gain(2)
        self.chA.set_coupling_dc()
        self.chA.set_ch_on()
        self.chA.send_settings()
        self.chA.set_offset(0)
        self.chA.set_nprom(1)
        self.chA.set_clk_divisor(1)

        self.chB.set_attenuator(3)
        self.chB.set_gain(4)
        self.chB.set_coupling_dc()
        self.chB.set_ch_on()
        self.chB.send_settings()
        self.chB.set_offset(0)
        self.chB.set_nprom(1)
        self.chB.set_clk_divisor(1)

        self.set_trigger_mode_normal()

        return

if __name__ == "__main__":
    oscope = Smartbench()
