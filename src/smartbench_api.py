
from pyftdi.ftdi import Ftdi
import time

# FTDI bridge driver
ft = Ftdi()
ft.open(vendor=0x0403,product=0x6010,interface=2)

def __send( addr, data ):
    ft.write_data( addr )
    ft.write_data( data )

# REGISTERS ADDRESSES (PRIVATE)
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

# BIT FIELD of SETTINGS_CHA, SETTINGS_CHB (PRIVATE)
__CONF_CH_ATT = 5 # starting bit of ATT field.
__CONF_CH_GAIN = 2
__CONF_CH_DC_COUPLING = 1
__CONF_CH_ON = 0

# BIT FIELD of TRIGGER CONF REG
__TRIGGER_CONF_SOURCE_SEL = 1
__TRIGGER_CONF_EDGE = 0

# BIT FIELD of Requests handler
__RQST_START_IDX = 0
__RQST_STOP_IDX = 1
__RQST_CHA_IDX = 2
__RQST_CHB_IDX = 3
__RQST_TRIG_IDX = 4
__RQST_RST_IDX = 5

class Smartbench:



    __trigger_settings = 0
    __triger_value_register = 2 ^ 7
    __num_samples = 256
    __pretrigger = 0

    # Channel register instance
    chA = channel(0)
    chB = channel(1)

    # __init__ ( self ):
    #     self.__ft.open(vendor=0x0403,product=0x6010,interface=2)

    get_pretrigger( self ):
        return self.__pretrigger

    set_pretrigger( self, pt_value ):
        self.__pretrigger = pt_value
        __send( __ADDR_PRETRIGGER, self.__pretrigger )


class __Channel:

    # __nchannel is:
    # 0 -> channel A
    # 1 -> channel B
    __nchannel

    # FPGAs register values.
    # Use methods to get/set actual values.
    __requests = 0
    __settings = 0xE1
    __dac_value = 2 ^ 9
    __nprom = 0
    __clk_divisor = 4

    __init__( self, channel_number ):
        self.__nchannel = channel_number

    # channel settings
    get_attenuator( self ):
        return ( self.__settings >> 5) & 7

    set_attenuator( self, att ):
        if att<8 and att>=0:
            self.__settings |= att << 5

    get_gain( self ):
        return ( self.__settings >> 2 ) & 7

    set_gain( self, gain ):
        if gain<8 and gain>=0:
            self.__settings |= gain << 2

    set_coupling_dc( self ):
        self.__settings |= 2

    set_coupling_ac( self ):
        self.__settings &= 253

    set_ch_on( self ):
        self.__settings |= 1

    set_ch_off( self ):
        self.__settings &= 254

    send_settings( self ):
        __send( __ADDR_SETTINGS_CHA + self.__nchannel, self.__settings )

    # Offset value
    get_offset( self ):
        return self.__dac_value - 2^9

    set_offset( self, val ):
        self.__dac_value = val + 2^9
        __send( __ADDR_DAC_CHA + self.__nchannel, self.__dac_value )

    get_nprom( self ):
        return __nprom + 1

    set_nprom( self, n ):
        self.__nprom = n - 1
        __send( __ADDR_N_MOVING_AVERAGE_CHA + self.__nchannel, self.__nprom )

    get_clk_divisor( self ):
        return self.__clk_divisor+1

    set_clk_divisor( self, div ):
        self.__clk_divisor = div-1
        __send( __ADDR_ADC_CLK_DIV_CHA_L + self.__nchannel, self.__clk_divisor&0xFFFF )
        __send( __ADDR_ADC_CLK_DIV_CHA_H + self.__nchannel, (self.__clk_divisor>>16)&0xFFFF )



# i = 1
# while True:
#     i = (i*2)%255
#     print(ft.write_data(bytes([i])),i)
#     time.sleep(0.5)
