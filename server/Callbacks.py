
from Configuration_Definitions import *
from SmartbenchApp import *
from OscopeApi import *


def update_on(active, tgl, channel):
    #if(active is True):
    if ( channel.is_ch_on() ):
        channel.set_ch_off()
        tgl.label = "CHA: ON"
    else:
        channel.set_ch_on()
        tgl.label = "CHA: OFF"
    print("UPDATED ON")
    return

def update_scale(idx, drpdwn, channel):
    channel.set_attenuator(
        Configuration_Definitions.Att_Sel[idx] )
    channel.set_gain(
        Configuration_Definitions.Gain_Sel[idx] )
    print("idx={}".format(idx))
    drpdwn.label = Configuration_Definitions.voltage_scales_str[idx]
    print("UPDATED SCALE")
    return

def update_dc_coupling(dc, tgl, channel):
    if(dc is True):
        channel.set_coupling_dc()
        tgl.label = "Coupling: DC"
    else:
        channel.set_coupling_ac()
        tgl.label = "Coupling: AC"
    print("UPDATED COUPLING")
    return


def update_trigger_run(attrname, old, new):
    print("Completar Kuku")

def update_trigger_source(attrname, old, new):
    print("Completar Kuku")

def update_trigger_edge(attrname, old, new):
    print("Completar Kuku")

def update_pre_trigger(attrname, old, new):
    print("Completar Kuku")

def update_trigger_val(attrname, old, new):
    print("Completar Kuku")

def update_trigger_type(attrname, old, new):
    print("Completar Kuku")

def update_horizontal(attrname, old, new):
    print("Completar Kuku")
