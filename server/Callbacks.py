
from Configuration_Definitions import *
from SmartbenchApp import *
from OscopeApi import *


def update_on(active, tgl, channel):
    if ( channel.is_ch_on() ):
        channel.set_ch_off()
        tgl.label = "CHA: ON"
    else:
        channel.set_ch_on()
        tgl.label = "CHA: OFF"
    print("UPDATED ON")
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

def update_scale(idx, drpdwn, channel):
    channel.set_attenuator(
        Configuration_Definitions.Att_Sel[idx] )
    channel.set_gain(
        Configuration_Definitions.Gain_Sel[idx] )
    drpdwn.label = Configuration_Definitions.voltage_scales_str[idx]
    print("Updated scale V - idx = {}".format(idx))
    return

def update_trigger_run(tgl, app):
    if(app.isRunning()):
        app.stop()
        tgl.label = "Run"
    else:
        app.start()
        tgl.label = "Stop"
    print("Updated Trigger Run")
    return

def update_trigger_source(tgl, app):
    if(app.smartbench.get_trigger_source() == app.smartbench.TRIGGER_SOURCE_CHA):
        app.smartbench.set_trigger_source_chb()
        tgl.label = "Source: CHB"
    elif(app.smartbench.get_trigger_source() == app.smartbench.TRIGGER_SOURCE_CHB):
        app.smartbench.set_trigger_source_cha()
        tgl.label = "Source: CHA"
    print("Updated Trigger Source. {}".format(app.smartbench.get_trigger_source()))

def update_trigger_edge(tgl, app):
    print("Completar Kuku")

def update_pre_trigger(value, app):
    app.smartbench.set_pretrigger(value)
    print("Updated pre-trigger")

def update_trigger_val(value, app):
    app.smartbench.set_trigger_value(value)
    print("Updated Trigger Value")

def update_trigger_type(idx, drpdwn, app):
    if(idx == 0): # mode Auto
        app.smartbench.set_trigger_mode_auto()
    elif (idx == 1):
        app.smartbench.set_trigger_mode_normal()
    else: # Single
        app.getSingleSeq()
    Configuration_Definitions.trigger_type_str[idx]
    drpdwn.label = Configuration_Definitions.trigger_type_str[idx]
    print("Updated trigger type - idx = {}".format(idx))

def update_horizontal(attrname, old, new):
    print("Completar Kuku")
