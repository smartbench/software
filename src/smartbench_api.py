
from pyftdi.ftdi import Ftdi
#import time

#######################################################
################## FTDI bridge driver #################
#######################################################

ft = Ftdi()
ft.open(vendor=0x0403,product=0x6010,interface=2)

def __send( addr, data ):
    ft.write_data( addr )
    ft.write_data( data )

#######################################################
################# LIBRARY DEFINITIONS #################
#######################################################

### REGISTERS ADDRESSES ###

# CHB addresses not unused
# always used __ADDR_XXX_CHA + __nchanel where __nchanel is 0 for channel A and 1 for channel B.

__ADDR_REQUESTS = 0
__ADDR_SETTINGS_CHA = 1
__ADDR_SETTINGS_CHB = 2
__ADDR_DAC_CHA = 3
__ADDR_DAC_CHB = 4
__ADDR_TRIGGER_SETTINGS = 5
__ADDR_TRIGGER_VALUE = 6
__ADDR_NUM_SAMPLES = 7
__ADDR_PRETRIGGER = 8
__ADDR_ADC_CLK_DIV_CHA_L = 9
__ADDR_ADC_CLK_DIV_CHA_H = 10
__ADDR_ADC_CLK_DIV_CHB_L = 11
__ADDR_ADC_CLK_DIV_CHB_H = 12
__ADDR_N_MOVING_AVERAGE_CHA = 13
__ADDR_N_MOVING_AVERAGE_CHB = 14

### BIT FIELDS ###
# DEFINES ARE THE INITIAL BIT NUMBER OF THIS FIELD

# SETTINGS_CHA, SETTINGS_CHB
__CONF_CH_ATT = 5
__CONF_CH_GAIN = 2
__CONF_CH_DC_COUPLING = 1
__CONF_CH_ON = 0

# TRIGGER CONF REG
__TRIGGER_CONF_SOURCE_SEL = 1
__TRIGGER_CONF_EDGE = 0

# Requests handler
__RQST_START_IDX = 0
__RQST_STOP_IDX = 1
__RQST_CHA_IDX = 2
__RQST_CHB_IDX = 3
__RQST_TRIG_IDX = 4
__RQST_RST_IDX = 5

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

### WIDTH DEFINITIONS ###
__ADC_WIDTH = 8
__DAC_WIDTH = 10
__ADDR_WIDTH = 8

#######################################################
#################### CHANNEL CLASS ####################
#######################################################

class __Channel:

    # __nchannel is:
    # 0 -> channel A
    # 1 -> channel B
    __nchannel

    # FPGAs register values.
    # Use methods to get/set actual values.
    __requests = 0
    __settings = 0xE1
    __dac_value = 2 ^ ( __DAC_WIDTH - 1 )
    __nprom = 0
    __clk_divisor = 3

    def __init__( self, channel_number ):
        self.__nchannel = channel_number

    # channel settings
    def get_attenuator( self ):
        return ( self.__settings >> __CONF_CH_ATT ) & 0x7

    def set_attenuator( self, att ):
        if att<8 and att>=0:
            self.__settings &= ~( 0x7 << __CONF_CH_ATT )
            self.__settings |= att << __CONF_CH_ATT
        else:
            print "Attenuation selector must be a number between 0 and 7"

    def get_gain( self ):
        return ( self.__settings >> __CONF_CH_GAIN ) & 0x7

    def set_gain( self, gain ):
        if gain<8 and gain>=0:
            self.__settings &= ~( 0x7 << __CONF_CH_GAIN )
            self.__settings |= gain << __CONF_CH_GAIN
        else:
            print "Gain selector must be a number between 0 and 7"

    def get_coupling( self ):
        return ( self.__settings >> __CONF_CH_DC_COUPLING ) & 0x1

    def set_coupling_dc( self ):
        self.__settings &= ~( 1 << __CONF_CH_DC_COUPLING )

    def set_coupling_ac( self ):
        self.__settings |= 1 << __CONF_CH_DC_COUPLING

    def get_ch_status( self ):
        return ( self.__setting >> __CONF_CH_ON ) & 0x1

    def set_ch_on( self ):
        self.__settings |= 1 << __CONF_CH_ON

    def set_ch_off( self ):
        self.__settings &= ~(1 << __CONF_CH_ON)

    def send_settings( self ):
        __send( __ADDR_SETTINGS_CHA + self.__nchannel, self.__settings )

    # Offset value
    def get_offset( self ):
        return self.__dac_value - 2^( DAC_WIDTH-1 )

    def set_offset( self, val ):
        self.__dac_value = val + 2^( DAC_WIDTH-1 )
        __send( __ADDR_DAC_CHA + self.__nchannel, self.__dac_value )

    def get_nprom( self ):
        return __nprom + 1

    def set_nprom( self, n ):
        self.__nprom = n - 1
        __send( __ADDR_N_MOVING_AVERAGE_CHA + self.__nchannel, self.__nprom )

    def get_clk_divisor( self ):
        return self.__clk_divisor+1

    def set_clk_divisor( self, div ):
        self.__clk_divisor = div-1
        __send( __ADDR_ADC_CLK_DIV_CHA_L + self.__nchannel, self.__clk_divisor&0xFFFF )
        __send( __ADDR_ADC_CLK_DIV_CHA_H + self.__nchannel, (self.__clk_divisor>>16)&0xFFFF )

#######################################################
##################### OSCOPE CLASS ####################
#######################################################

class Smartbench:

    __trigger_settings = ( TRIGGER_SOURCE_CHA << __TRIGGER_CONF_SOURCE_SEL ) | ( POSITIVE_EDGE << __TRIGGER_CONF_EDGE )
    __triger_value = 2 ^ ( __ADC_WIDTH-1 )
    __num_samples = 100
    __pretrigger = 0

    # Channel register instance
    chA = channel(0)
    chB = channel(1)

    def request_start( self ):
        __send( __ADDR_REQUESTS, 1 << __RQST_START_IDX )

    def request_stop( self ):
        __send( __ADDR_REQUESTS, 1 << __RQST_STOP_IDX )

    def request_chA( self ):
        __send( __ADDR_REQUESTS, 1 << __RQST_CHA_IDX )

    def request_chB( self ):
        __send( __ADDR_REQUESTS, 1 << __RQST_CHB_IDX )

    def request_trigger_status( self ):
        __send( __ADDR_REQUESTS, 1 << __RQST_TRIG_IDX )

    def request_reset( self ):
        __send( __ADDR_REQUESTS, 1 << __RQST_RST_IDX )

    def get_trigger_edge( self ):
        return ( self.__trigger_settings >> __TRIGGER_CONF_EDGE ) & 0x1

    def set_trigger_posedge( self ):
        self.__trigger_settings &= ~( 1 << __TRIGGER_CONF_EDGE )

    def set_trigger_negedge( self ):
        self.__trigger_settings |= ( 1 << __TRIGGER_CONF_EDGE )

    def get_trigger_source( self ):
        return ( self.__trigger_settings >> __TRIGGER_CONF_SOURCE_SEL ) & 0x3

    def set_trigger_source_cha( self ):
        self.__trigger_settings &= 0x3 << __TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= TRIGGER_SOURCE_CHA << __TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_chb( self ):
        self.__trigger_settings &= 0x3 << __TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= TRIGGER_SOURCE_CHB << __TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_ext( self ):
        self.__trigger_settings &= 0x3 << __TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= TRIGGER_SOURCE_EXT << __TRIGGER_CONF_SOURCE_SEL

    def send_trigger_settings( send ):
        __send( __ADDR_TRIGGER_SETTINGS, self.__trigger_settings )

    def get_trigger_value( self, val ):
        return self.__trigger_value - 2^(__ADC_WIDTH-1)

    def set_trigger_value( self, val ):
        self.__trigger_value = 2^(__ADC_WIDTH-1) + val
        __send( __ADDR_TRIGGER_VALUE, self.__trigger_value )

    def get_number_of_samples( self ):
        return self.__num_samples

    def set_number_of_samples( self, N ):
        self.__num_samples = N
        __send( __ADDR_NUM_SAMPLES, self.__num_samples )

    def get_pretrigger( self ):
        return self.__pretrigger

    def set_pretrigger( self, pt_value ):
        self.__pretrigger = pt_value
        __send( __ADDR_PRETRIGGER, self.__pretrigger )
