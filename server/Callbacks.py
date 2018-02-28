
import SmartbenchApp
import OscopeApi


def update_on(active, label, channel):
    #if(active is True):
    if ( channel.get_ch_status() == _CHANNEL_ON):
        channel.set_ch_off()
        label = "CHA: ON"
    else:
        channel.set_ch_on()
        label = "CHA: OFF"
    return

def update_scale(idx, label, channel):
    channel.set_attenuator(
        Configuration_Definitions.Att_Sel(idx) )
    channel.set_gain(
        Configuration_Definitions.Gain_Sel(idx) )
    label = Configuration_Definitions.voltage_scales_str(idx)
    return

def update_dc_coupling(dc, label, channel):
    if(dc is True):
        channel.set_coupling_dc()
        label = "Coupling: DC"
    else:
        channel.set_coupling_ac()
        label = "Coupling: AC"
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
