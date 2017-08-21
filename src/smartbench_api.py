#!/usr/bin/python3

from pyftdi.ftdi import Ftdi
#import time

#######################################################
################## FTDI bridge driver #################
#######################################################

class _Oscope_ftdi( Ftdi ):

    __BYTEORDER = "little" # "big"

    def open( self ):
        dev_list = self.find_all([(0x0403,0x6010)],True)
        if(len(dev_list) > 0):
            print ("Device found:\n\t", dev_list)
            self.open(vendor=0x0403,product=0x6010,interface=2)
            print("Opened device!")
        else:
            print ("Device not connected!")

    def send( self, addr, data ):
        self.write_data( addr.to_bytes( 2, byteorder=__BYTEORDER ) )
        self.write_data( data.to_bytes( 2, byteorder=__BYTEORDER ) )

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

    COUPLING_AC = 1
    COUPLING_DC = 0

#######################################################
#################### CHANNEL CLASS ####################
#######################################################

class _Channel( _Definitions, _Oscope_ftdi ):

    def __init__( self, channel_number ):
        # __nchannel is:
        # 0 -> channel A
        # 1 -> channel B
        self.__nchannel = channel_number
        # FPGAs register values.
        # Use methods to get/set actual values.
        self.__requests = 0
        self.__settings = 0xE1
        self.__dac_value = 2 ^ ( self._DAC_WIDTH - 1 )
        self.__nprom = 0
        self.__clk_divisor = 3

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
        self.send( self._ADDR_SETTINGS_CHA + self.__nchannel, self.__settings )

    # Offset value
    def get_offset( self ):
        return self.__dac_value - 2^( self._DAC_WIDTH-1 )

    def set_offset( self, val ):
        self.__dac_value = val + 2^( self._DAC_WIDTH-1 )
        self.send( self._ADDR_DAC_CHA + self.__nchannel, self.__dac_value )

    def get_nprom( self ):
        return __nprom + 1

    def set_nprom( self, n ):
        self.__nprom = n - 1
        self.send( self._ADDR_N_MOVING_AVERAGE_CHA + self.__nchannel, self.__nprom )

    def get_clk_divisor( self ):
        return self.__clk_divisor+1

    def set_clk_divisor( self, div ):
        self.__clk_divisor = div-1
        self.send( self._ADDR_ADC_CLK_DIV_CHA_L + self.__nchannel, self.__clk_divisor&0xFFFF )
        self.send( self._ADDR_ADC_CLK_DIV_CHA_H + self.__nchannel, (self.__clk_divisor>>16)&0xFFFF )

#######################################################
##################### OSCOPE CLASS ####################
#######################################################

class Smartbench( _Definitions, _Oscope_ftdi ):

    def __init__( self ):

        self.open()
        self.__trigger_settings = ( self.TRIGGER_SOURCE_CHA << self._TRIGGER_CONF_SOURCE_SEL ) | ( self.POSITIVE_EDGE << self._TRIGGER_CONF_EDGE )
        self.__triger_value = 2 ^ ( self._ADC_WIDTH-1 )
        self.__num_samples = 100
        self.__pretrigger = 0

        # Channel register instance
        self.chA = _Channel(0)
        self.chB = _Channel(1)

    def request_start( self ):
        self.send( self._ADDR_REQUESTS, 1 << self._RQST_START_IDX )

    def request_stop( self ):
        self.send( self._ADDR_REQUESTS, 1 << self._RQST_STOP_IDX )

    def request_chA( self ):
        self.send( self._ADDR_REQUESTS, 1 << self._RQST_CHA_IDX )

    def request_chB( self ):
        self.send( self._ADDR_REQUESTS, 1 << self._RQST_CHB_IDX )

    def request_trigger_status( self ):
        self.send( self._ADDR_REQUESTS, 1 << self._RQST_TRIG_IDX )

    def request_reset( self ):
        self.send( self._ADDR_REQUESTS, 1 << self._RQST_RST_IDX )

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

    def send_trigger_settings( send ):
        self.send( self._ADDR_TRIGGER_SETTINGS, self.__trigger_settings )

    def get_trigger_value( self, val ):
        return self.__trigger_value - 2^( self._ADC_WIDTH-1 )

    def set_trigger_value( self, val ):
        self.__trigger_value = 2^( self._ADC_WIDTH-1 ) + val
        self.send( self._ADDR_TRIGGER_VALUE, self.__trigger_value )

    def get_number_of_samples( self ):
        return self.__num_samples

    def set_number_of_samples( self, N ):
        self.__num_samples = N
        self.send( self._ADDR_NUM_SAMPLES, self.__num_samples )

    def get_pretrigger( self ):
        return self.__pretrigger

    def set_pretrigger( self, pt_value ):
        self.__pretrigger = pt_value
        self.send( self._ADDR_PRETRIGGER, self.__pretrigger )

if __name__ == "__main__":
    oscope = Smartbench()
