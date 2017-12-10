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

    __BYTEORDER = 'little' # 'big' # 'big' / 'little'
    status = 'closed'

    def __init__(self,**kwargs):
        self.ftdi = 0
        pass

    def open( self, device='/dev/ttyUSB1' ):
        try:
            self.ftdi = serial.Serial(device, baudrate=921600, timeout=2)
            print("Opened device!")
            return True
        except:
            print ("Device not connected!")
            return False
        # if(self.ftdi.is_open):
        #     print("Opened device!")
        #     return True
        # else:
        #     print ("Device not connected!")
        #     return False

    def close(self):
        self.ftdi.close()
        print ("Device closed.")

    def send( self, addr, data ):
        aux = bytes( [ int(addr) , int(data%256) , int((data>>8)%256) ] )
        n = self.ftdi.write( aux )
        print("written {} bytes: {}".format(len(list(aux)), aux))
        i = 0

    def receive(self, size, blocking=True, timeout=0):
        data = []
        if(blocking==True):
            if(timeout==0):
                while(len(data) < size):
                    data = data + list(self.ftdi.read(size - len(data)))
                    if(len(data)>0): pass # print ("data=", data)
                    else: print ("receiving...")
                    if(len(data) < size):   time.sleep(0.3)
                    #print ("a) data=", data)
            else:
                to = Timeout(timeout)
                while(len(data) < size and to.timeout == False):
                    data = data + list(self.ftdi.read(size - len(data)))
                    if(len(data) < size and to.timeout == False):   time.sleep(0.05)
                    #print ("b) data=", data)
                del to
        else:
            data = data + list(self.ftdi.read(size - len(data)))
            #print ("c) data=", data)
        #print (data)
        return data

    def empty_read_buffer():
        data = range(10)
        while (len(data) == 10): data = self.ftdi.read(10)


class Timeout (Timer):
    timeout = False
    def __init__(self, time, *args, **kwargs):
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
    # always used __ADDR_XXX_CHA + __nchanel where __nchanel is 0 for channel A and 1 for channel B.

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

#######################################################
#################### CHANNEL CLASS ####################
#######################################################

class _Channel( _Definitions ):

    def __init__( self, channel_number, oscope):
        # __nchannel is:
        # 0 -> channel A
        # 1 -> channel B
        self.__nchannel = channel_number
        # FPGAs register values.
        # Use methods to get/set actual values.
        self.__requests = 0
        self.__settings = 0xE1
        self.__dac_value = 2 ** ( self._DAC_WIDTH - 1 )
        self.__nprom = 0
        self.__clk_divisor = 3
        self.oscope = oscope

    # channel settings
    def get_attenuator( self ):
        return ( self.__settings >> self._CONF_CH_ATT ) & 0x7

    def set_attenuator( self, att ):
        if att<8 and att>=0:
            self.__settings &= ~( 0x7 << self._CONF_CH_ATT )
            self.__settings |= att << self._CONF_CH_ATT
        else:
            print( "Attenuation selector must be a number between 0 and 7" )

    def get_gain( self ):
        return ( self.__settings >> __CONF_CH_GAIN ) & 0x7

    def set_gain( self, gain ):
        if gain<8 and gain>=0:
            self.__settings &= ~( 0x7 << self._CONF_CH_GAIN )
            self.__settings |= gain << self._CONF_CH_GAIN
        else:
            print( "Gain selector must be a number between 0 and 7" )

    def get_coupling( self ):
        return ( self.__settings >> self._CONF_CH_DC_COUPLING ) & 0x1

    def set_coupling_dc( self ):
        self.__settings &= ~( 1 << self._CONF_CH_DC_COUPLING )

    def set_coupling_ac( self ):
        self.__settings |= 1 << self._CONF_CH_DC_COUPLING

    def get_ch_status( self ):
        return ( self.__setting >> self._CONF_CH_ON ) & 0x1

    def set_ch_on( self ):
        self.__settings |= 1 << self._CONF_CH_ON

    def set_ch_off( self ):
        self.__settings &= ~(1 << self._CONF_CH_ON)

    def send_settings( self ):
        self.oscope.send( self._ADDR_SETTINGS_CHA + self.__nchannel, self.__settings )

    # Offset value
    def get_offset( self ):
        return self.__dac_value - 2**( self._DAC_WIDTH-1 )

    def set_offset( self, val ):
        self.__dac_value = val + 2**( self._DAC_WIDTH-1 )
        self.oscope.send( self._ADDR_DAC_CHA + self.__nchannel, self.__dac_value )

    # Documentation for nprom:
    # Prom  Fpga_value
    # 1     0
    # 2     1
    # 4     2
    # 8     3
    # ...
    def get_nprom( self ):
        return int(2 ** __nprom)

    def set_nprom( self, n ):
        self.__nprom = int(log(n,2))
        self.oscope.send( self._ADDR_N_MOVING_AVERAGE_CHA + self.__nchannel, self.__nprom )

    def get_clk_divisor( self ):
        return self.__clk_divisor+1

    def set_clk_divisor( self, div ):
        self.__clk_divisor = div-1
        self.oscope.send( self._ADDR_ADC_CLK_DIV_CHA_L + self.__nchannel, self.__clk_divisor&0xFFFF )
        self.oscope.send( self._ADDR_ADC_CLK_DIV_CHA_H + self.__nchannel, (self.__clk_divisor>>16)&0xFFFF )

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
        self.__trigger_settings = ( self.TRIGGER_SOURCE_CHA << self._TRIGGER_CONF_SOURCE_SEL ) | ( self.POSITIVE_EDGE << self._TRIGGER_CONF_EDGE )
        self.__triger_value = 2 ** ( self._ADC_WIDTH-1 )
        self.__num_samples  = 100
        self.__pretrigger   = 0
        self.__trigger_mode = self.MODE_NORMAL

        # Channel register instance
        self.chA = _Channel(0, self.oscope)
        self.chB = _Channel(1, self.oscope)


    def get_oscope_status (self):
        return (self.oscope_status)

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
        if(n==0): n = self.__num_samples
        return self.oscope.receive(n, blocking=True)

    def get_trigger_edge( self ):
        return ( self.__trigger_settings >> self._TRIGGER_CONF_EDGE ) & 0x1

    def set_trigger_posedge( self ):
        self.__trigger_settings &= ~( 1 << self._TRIGGER_CONF_EDGE )

    def set_trigger_negedge( self ):
        self.__trigger_settings |= ( 1 << self._TRIGGER_CONF_EDGE )

    def get_trigger_source( self ):
        return ( self.__trigger_settings >> self._TRIGGER_CONF_SOURCE_SEL ) & 0x3

    def set_trigger_source_cha( self ):
        self.__trigger_settings &= 0x3 << self._TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= self.TRIGGER_SOURCE_CHA << self._TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_chb( self ):
        self.__trigger_settings &= 0x3 << self._TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= self.TRIGGER_SOURCE_CHB << self._TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_ext( self ):
        self.__trigger_settings &= 0x3 << self._TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= self.TRIGGER_SOURCE_EXT << self._TRIGGER_CONF_SOURCE_SEL

    def send_trigger_settings( self ):
        self.oscope.send( self._ADDR_TRIGGER_SETTINGS, self.__trigger_settings )
        print("Trigger settings set to {}".format(hex(self.__trigger_settings) ) )

    def get_trigger_value( self ):
        return self.__trigger_value# - 2**( self._ADC_WIDTH-1 )

    def set_trigger_value( self, val ):
        self.__trigger_value = (1 << self._ADC_WIDTH-1 ) + val
        self.oscope.send( self._ADDR_TRIGGER_VALUE, self.__trigger_value )
        print("Trigger value set to {}".format(self.__trigger_value))

    def get_number_of_samples( self ):
        return self.__num_samples

    def set_number_of_samples( self, N ):
        self.__num_samples = N
        self.oscope.send( self._ADDR_NUM_SAMPLES, self.__num_samples )
        print("Num_samples set to {}".format(self.__num_samples))

    def get_pretrigger( self ):
        return self.__pretrigger

    def set_pretrigger( self, pt_value ):
        self.__pretrigger = pt_value
        self.oscope.send( self._ADDR_PRETRIGGER, self.__pretrigger )
        print("Pretrigger set to {}".format(self.__pretrigger))

    def set_trigger_mode( self, mode ):
        self.__trigger_mode = mode

    def set_trigger_mode_single ( self ): self.set_trigger_mode(self.MODE_SINGLE)
    def set_trigger_mode_normal ( self ): self.set_trigger_mode(self.MODE_NORMAL)
    def set_trigger_mode_auto   ( self ): self.set_trigger_mode(self.MODE_AUTO)

    def get_trigger_mode( self ):
        return self.__trigger_mode

    def is_trigger_mode_single (self): return (self.__trigger_mode == self.MODE_SINGLE)
    def is_trigger_mode_normal (self): return (self.__trigger_mode == self.MODE_NORMAL)
    def is_trigger_mode_auto   (self): return (self.__trigger_mode == self.MODE_AUTO)

if __name__ == "__main__":
    oscope = Smartbench()
