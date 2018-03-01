
from Configuration_Definitions import *
from SmartbenchApp import *
from OscopeApi import *


def update_on(active, tgl, channel):
    if ( channel.is_ch_on() ):
        channel.set_ch_off()
        tgl.label = "CHANNEL ON"
    else:
        channel.set_ch_on()
        tgl.label = "CHANNEL OFF"
    print("Updated channel on/off")
    return

def update_dc_coupling(dc, tgl, channel):
    if(dc is True):
        channel.set_coupling_dc()
        tgl.label = "Coupling: DC"
    else:
        channel.set_coupling_ac()
        tgl.label = "Coupling: AC"
    print("Updated coupling")
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
    if(app.smartbench.get_trigger_edge() == app.smartbench.POSITIVE_EDGE):
        app.smartbench.set_trigger_negedge()
        tgl.label = "Negative Edge"
    else:
        app.smartbench.set_trigger_posedge()
        tgl.label = "Positive Edge"
    print("Updated trigger edge")
    return


def update_pre_trigger(value, app):
    app.smartbench.set_pretrigger(value)
    print("Updated pre-trigger")

def update_trigger_val(value, app):
    app.smartbench.set_trigger_value(value)
    # change in plot
    print("Updated Trigger Value")

def update_trigger_type(idx, drpdwn, app):
    if(idx == 0): # mode Auto
        app.smartbench.set_trigger_mode_auto()
        #print("\n\nAUTO\n\n")
    elif (idx == 1):
        app.smartbench.set_trigger_mode_normal()
        #print("\n\nNORMAL\n\n")
    else: # Single
        app.getSingleSeq()
        #print("\n\nSINGLE\n\n")
    drpdwn.label = Configuration_Definitions.trigger_type_str[idx]
    print("Updated trigger type - idx = {}".format(idx))

def update_horizontal(idx, dwrdwn, app, pretrigger):
    app.smartbench.set_clk_divisor(
        Configuration_Definitions.Clock_Adc_Div_Sel[idx]
    )
    app.smartbench.set_nprom(
        Configuration_Definitions.Mov_Ave_Sel[idx]
    )

    N = Configuration_Definitions.Num_Samples[idx]
    app.smartbench.set_number_of_samples( N )
    app.plot.x_range.end = N-1
    #app.plot.xaxis[0].ticker=FixedTicker(ticks=np.arange(0,N-1,N/10))
    app.plot.xgrid[0].ticker=FixedTicker(ticks=np.arange(0,N-1,N/10))
    if(pretrigger.value > N-1):
        pretrigger.value = N-1
    pretrigger.end = N-1
    dwrdwn.label = Configuration_Definitions.timebase_scales_str[idx]+'/div'
    print("Updated BT. clk divider = {}\tprom = {}".format(
        Configuration_Definitions.Clock_Adc_Div_Sel[idx],
        Configuration_Definitions.Mov_Ave_Sel[idx]
    ))
