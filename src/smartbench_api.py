
from pyftdi.ftdi import Ftdi
#import time

#######################################################
################## FTDI bridge driver #################
#######################################################

ft = Ftdi()
#ft.open(vendor=0x0403,product=0x6010,interface=2)

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

    def __init__( self, channel_number ):

        global __DAC_WIDTH

        # __nchannel is:
        # 0 -> channel A
        # 1 -> channel B
        self.__nchannel = channel_number

        # FPGAs register values.
        # Use methods to get/set actual values.
        self.__requests = 0
        self.__settings = 0xE1
        self.__dac_value = 2 ^ ( __DAC_WIDTH - 1 )
        self.__nprom = 0
        self.__clk_divisor = 3

    # channel settings
    def get_attenuator( self ):
        global __CONF_CH_ATT
        return ( self.__settings >> __CONF_CH_ATT ) & 0x7

    def set_attenuator( self, att ):
        global __CONF_CH_ATT
        if att<8 and att>=0:
            self.__settings &= ~( 0x7 << __CONF_CH_ATT )
            self.__settings |= att << __CONF_CH_ATT
        else:
            print "Attenuation selector must be a number between 0 and 7"

    def get_gain( self ):
        global __CONF_CH_GAIN
        return ( self.__settings >> __CONF_CH_GAIN ) & 0x7

    def set_gain( self, gain ):
        global __CONF_CH_GAIN
        if gain<8 and gain>=0:
            self.__settings &= ~( 0x7 << __CONF_CH_GAIN )
            self.__settings |= gain << __CONF_CH_GAIN
        else:
            print "Gain selector must be a number between 0 and 7"

    def get_coupling( self ):
        global __CONF_CH_DC_COUPLING
        return ( self.__settings >> __CONF_CH_DC_COUPLING ) & 0x1

    def set_coupling_dc( self ):
        global __CONF_CH_DC_COUPLING
        self.__settings &= ~( 1 << __CONF_CH_DC_COUPLING )

    def set_coupling_ac( self ):
        global __CONF_CH_DC_COUPLING
        self.__settings |= 1 << __CONF_CH_DC_COUPLING

    def get_ch_status( self ):
        global __CONF_CH_ON
        return ( self.__setting >> __CONF_CH_ON ) & 0x1

    def set_ch_on( self ):
        global __CONF_CH_ON
        self.__settings |= 1 << __CONF_CH_ON

    def set_ch_off( self ):
        global __CONF_CH_ON
        self.__settings &= ~(1 << __CONF_CH_ON)

    def send_settings( self ):
        global __ADDR_SETTINGS_CHA
        __send( __ADDR_SETTINGS_CHA + self.__nchannel, self.__settings )

    # Offset value
    def get_offset( self ):
        global DAC_WIDTH
        return self.__dac_value - 2^( DAC_WIDTH-1 )

    def set_offset( self, val ):
        global DAC_WIDTH
        global __ADDR_DAC_CHA
        self.__dac_value = val + 2^( DAC_WIDTH-1 )
        __send( __ADDR_DAC_CHA + self.__nchannel, self.__dac_value )

    def get_nprom( self ):
        return __nprom + 1

    def set_nprom( self, n ):
        global __ADDR_N_MOVING_AVERAGE_CHA
        self.__nprom = n - 1
        __send( __ADDR_N_MOVING_AVERAGE_CHA + self.__nchannel, self.__nprom )

    def get_clk_divisor( self ):
        return self.__clk_divisor+1

    def set_clk_divisor( self, div ):
        global __ADDR_ADC_CLK_DIV_CHA_L
        global __ADDR_ADC_CLK_DIV_CHA_H
        self.__clk_divisor = div-1
        __send( __ADDR_ADC_CLK_DIV_CHA_L + self.__nchannel, self.__clk_divisor&0xFFFF )
        __send( __ADDR_ADC_CLK_DIV_CHA_H + self.__nchannel, (self.__clk_divisor>>16)&0xFFFF )

#######################################################
##################### OSCOPE CLASS ####################
#######################################################

class Smartbench:

    def __init__( self ):
        global TRIGGER_SOURCE_CHA
        global __TRIGGER_CONF_SOURCE_SEL
        global POSITIVE_EDGE
        global __TRIGGER_CONF_EDGE
        global __ADC_WIDTH

        self.__trigger_settings = ( TRIGGER_SOURCE_CHA << __TRIGGER_CONF_SOURCE_SEL ) | ( POSITIVE_EDGE << __TRIGGER_CONF_EDGE )
        self.__triger_value = 2 ^ ( __ADC_WIDTH-1 )
        self.__num_samples = 100
        self.__pretrigger = 0

        # Channel register instance
        self.chA = __channel(0)
        self.chB = __channel(1)

    def request_start( self ):
        global __ADDR_REQUESTS
        global __RQST_START_IDX
        __send( __ADDR_REQUESTS, 1 << __RQST_START_IDX )

    def request_stop( self ):
        global __ADDR_REQUESTS
        global __RQST_STOP_IDX
        __send( __ADDR_REQUESTS, 1 << __RQST_STOP_IDX )

    def request_chA( self ):
        global __ADDR_REQUESTS
        global __RQST_CHA_IDX
        __send( __ADDR_REQUESTS, 1 << __RQST_CHA_IDX )

    def request_chB( self ):
        global __ADDR_REQUESTS
        global __RQST_CHB_IDX
        __send( __ADDR_REQUESTS, 1 << __RQST_CHB_IDX )

    def request_trigger_status( self ):
        global __ADDR_REQUESTS
        global __RQST_TRIG_IDX
        __send( __ADDR_REQUESTS, 1 << __RQST_TRIG_IDX )

    def request_reset( self ):
        global __ADDR_REQUESTS
        global __RQST_RST_IDX
        __send( __ADDR_REQUESTS, 1 << __RQST_RST_IDX )

    def get_trigger_edge( self ):
        global __TRIGGER_CONF_EDGE
        return ( self.__trigger_settings >> __TRIGGER_CONF_EDGE ) & 0x1

    def set_trigger_posedge( self ):
        global __TRIGGER_CONF_EDGE
        self.__trigger_settings &= ~( 1 << __TRIGGER_CONF_EDGE )

    def set_trigger_negedge( self ):
        global __TRIGGER_CONF_EDGE
        self.__trigger_settings |= ( 1 << __TRIGGER_CONF_EDGE )

    def get_trigger_source( self ):
        global __TRIGGER_CONF_SOURCE_SEL
        return ( self.__trigger_settings >> __TRIGGER_CONF_SOURCE_SEL ) & 0x3

    def set_trigger_source_cha( self ):
        global __TRIGGER_CONF_SOURCE_SEL
        global TRIGGER_SOURCE_CHA
        self.__trigger_settings &= 0x3 << __TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= TRIGGER_SOURCE_CHA << __TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_chb( self ):
        global __TRIGGER_CONF_SOURCE_SEL
        global TRIGGER_SOURCE_CHB
        self.__trigger_settings &= 0x3 << __TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= TRIGGER_SOURCE_CHB << __TRIGGER_CONF_SOURCE_SEL

    def set_trigger_source_ext( self ):
        global __TRIGGER_CONF_SOURCE_SEL
        global TRIGGER_SOURCE_EXT
        self.__trigger_settings &= 0x3 << __TRIGGER_CONF_SOURCE_SEL
        self.__trigger_settings |= TRIGGER_SOURCE_EXT << __TRIGGER_CONF_SOURCE_SEL

    def send_trigger_settings( send ):
        global __ADDR_TRIGGER_SETTINGS
        __send( __ADDR_TRIGGER_SETTINGS, self.__trigger_settings )

    def get_trigger_value( self, val ):
        global __ADC_WIDTH
        return self.__trigger_value - 2^(__ADC_WIDTH-1)

    def set_trigger_value( self, val ):
        global __ADC_WIDTH
        global __ADDR_TRIGGER_VALUE
        self.__trigger_value = 2^(__ADC_WIDTH-1) + val
        __send( __ADDR_TRIGGER_VALUE, self.__trigger_value )

    def get_number_of_samples( self ):
        return self.__num_samples

    def set_number_of_samples( self, N ):
        global __ADDR_NUM_SAMPLES
        self.__num_samples = N
        __send( __ADDR_NUM_SAMPLES, self.__num_samples )

    def get_pretrigger( self ):
        return self.__pretrigger

    def set_pretrigger( self, pt_value ):
        global __ADDR_PRETRIGGER
        self.__pretrigger = pt_value
        __send( __ADDR_PRETRIGGER, self.__pretrigger )
