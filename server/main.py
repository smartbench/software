'''
To run the server

    bokeh serve WebApp.py

Then navigate to the URL

    http://localhost:5006/WebApp

in your browser.

To run the server on a specific port,

    bokeh serve WebApp.py --port <port number>
    http://localhost:<port number>/WebApp

'''
import numpy as np
import glob
from math import log

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.layouts import Spacer
from bokeh.models.widgets import Slider, TextInput, Button, Toggle, Dropdown
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure
from bokeh.palettes import Viridis3
from bokeh.models.widgets import Div

from tornado import gen
import tornado

from OscopeApi import *
from Configuration_Definitions import *
from SmartbenchApp import *

AUTORS = '''<hr><h1>Authors</h1>
<p> Nahuel Carducci </p>
<p> Andres Demski </p>
<p> Ariel Kukulanski </p>
<p> Ivan Paunovic </p>
'''

_STATUS_STOPPED = 0
_STATUS_RUNNING = 1

_CHANNEL_ON     = 1
_CHANNEL_OFF    = 0

MODE='scale_width'
DEFAULT_WIDTH = 300

# Set up data
N = 200
x = np.linspace(0, 10, N)
y_sin = np.sin(x)
y_cos = np.cos(x)
source_chA = ColumnDataSource(data=dict(x=x, y=y_sin))
source_chB = ColumnDataSource(data=dict(x=x, y=y_cos))
doc = curdoc()

escV = [(str(x),str(i)) for i,x in enumerate(Configuration_Definitions.voltage_scales_str)]
escT = [(str(x)+'/div',str(i)) for i,x in enumerate(Configuration_Definitions.timebase_scales_str)]

trig_types = [(s,str(i)) for i,s in enumerate(Configuration_Definitions.trigger_type_str)]

trig_line = ColumnDataSource(data=dict(x=(0,10), y=np.ones(2)*0.5))


# Set up plot
plot = figure(plot_width= 10,
              plot_height= 10,
              sizing_mode='scale_both',
              title="",
              tools="crosshair,pan,reset,save,wheel_zoom",
              )

plot.line('x', 'y', source=trig_line, line_width=1, line_alpha=0.8, color="yellow")
plot.line('x', 'y', source=source_chA, line_width=4, line_alpha=0.8, color="#CC00FB")
plot.line('x', 'y', source=source_chB, line_width=4, line_alpha=0.8, color="#00CCAA")

#### ESTO ES PAR SETEAR LA GRID, me falto los minorticks y sin eso no queda bien

#plot.xaxis[0].ticker=FixedTicker(ticks=np.arange(0,10,1))
#plot.xgrid[0].ticker=FixedTicker(ticks=np.arange(0,10,1))
#plot.yaxis[0].ticker=FixedTicker(ticks=np.arange(-4,+4,1))
#plot.ygrid[0].ticker=FixedTicker(ticks=np.arange(-4,+4,1))

Nsamp = 200
plot.x_range = Range1d(0, Nsamp-1)
plot.y_range = Range1d(0,255)

plot.xaxis[0].ticker=FixedTicker(ticks=np.arange(0,Nsamp-1,Nsamp/10))   #10 div
plot.xgrid[0].ticker=FixedTicker(ticks=np.arange(0,Nsamp-1,Nsamp/10))
#change yaxis ticker & ygrid ticker with fixed-width spacing
plot.yaxis[0].ticker=FixedTicker(ticks=np.arange(0,255,256/10))   #10 div
plot.ygrid[0].ticker=FixedTicker(ticks=np.arange(0,255,256/10))

# https://bokeh.pydata.org/en/latest/docs/user_guide/styling.html
#legend, grid, xgrid, ygrid, axis, xaxis, yaxis
plot.legend.location = "top_right"
#plot.xaxis.axis_label = "Tiempo []"
#plot.yaxis.axis_label = "Tensión []"

######## Func ###########
def list_ttys ():
    ttys = glob.glob('/dev/ttyUSB*')
    return [ (tty,tty) for i,tty in enumerate(ttys) ]

########## Callbacks #############
import Callbacks as cb
app = SmartbenchApp(doc, plot, source_chA, source_chB)

def update_on_cha(value):
    cb.update_on(value, on_cha, app.smartbench.chA)

def update_dc_coupling_cha(value):
    cb.update_dc_coupling(value, dc_coupling_cha, app.smartbench.chA)

def update_scale_cha(attrname, old, new):
    cb.update_scale(int(new), scale_cha, app.smartbench.chA)

def update_on_chb(value):
    cb.update_on(value, on_chb, app.smartbench.chB)

def update_dc_coupling_chb(value):
    cb.update_dc_coupling(value, dc_coupling_chb, app.smartbench.chB)

def update_scale_chb(attrname, old, new):
    cb.update_scale(int(new), scale_chb, app.smartbench.chB)

def update_trigger_run(value):
    cb.update_trigger_run(trigger_run, app)

def update_trigger_source(value):
    cb.update_trigger_source(trigger_source, app)

def update_trigger_edge(value):
    cb.update_trigger_edge(trigger_edge, app)

def update_pre_trigger(attrname, old, new):
    cb.update_pre_trigger(new, app)

def update_trigger_val(attrname, old, new):
    cb.update_trigger_val(new, app)

def update_trigger_type(attrname, old, new):
    cb.update_trigger_type(int(new), trigger_type, app)

def update_horizontal(attrname, old, new):
    cb.update_horizontal(int(new), horizontal, app, pre_trigger)

def update_but_connect(value):
    print ("Entered into update_but_connect")
    if but_connect.label == 'Connect':
        if app.smartbench.open(devices.label) is True :
            but_connect.label = 'Disconnect'
    else:
        app.smartbench.close()
        #but_connect.label = 'Connect'


def update_but_refresh(value):
    devices.menu = list_ttys()
    if len(devices.menu)==0:
        devices.value = 'Device'
    update_devices(devices.value)


def update_devices(value):
    devices.label = value

def update_status():
    if app.isRunning():
        trigger_run.label = "Stop"
    else:
        trigger_run.label = "Run"
    print("Updated Button Label to {}".format(trigger_run.label))
    return

def update_port_closed():
    print ("Entered port_closed callback")
    update_but_refresh(0)
    but_connect.label = 'Connect'
    printDebug ("Exited from port_closed callback")
    return


###### Layout funcs ######

def channel_layout(text,on, coupling, vert_gain):
    lay = column([text,row([on,coupling, vert_gain], sizing_mode=MODE, width=DEFAULT_WIDTH)],sizing_mode=MODE)
    return lay

def trigger_layout(text, run, ttype, source, edge, trigger, pretrigger ):
    lay = column([text,row([run,ttype,source, edge], sizing_mode=MODE, width=DEFAULT_WIDTH),trigger,pretrigger],sizing_mode=MODE)
    return lay

###### CONNECT ##########

but_connect = Toggle(label='Connect', active = True,sizing_mode='stretch_both')
but_connect.on_click( update_but_connect)
app.set_port_closed_callback(update_port_closed)

devices    = Dropdown(label="Device", menu = list_ttys(), disabled = False )
devices.on_click(update_devices)

but_refresh = Toggle(label='Refresh', active = True,sizing_mode='stretch_both')
but_refresh.on_click( update_but_refresh)

connect_layout = row([but_connect,devices,but_refresh],sizing_mode=MODE)

###### CHANNEL A ########

text_cha    = Div(text='<hr><h2>Channel A</h2>')
on_cha = Toggle(label='On/Off', active = True)
on_cha.on_click( update_on_cha)

scale_cha    = Dropdown(label="Scale A", menu = escV, disabled = False )
scale_cha.on_change('value',update_scale_cha)

dc_coupling_cha = Toggle(label="Coupling: DC", active = True)
dc_coupling_cha.on_click(update_dc_coupling_cha)

cha_layout = channel_layout(text_cha,on_cha, dc_coupling_cha, scale_cha)

####### CHANNEL B ########

text_chb    = Div(text='<hr><h2>Channel B</h2>')
on_chb = Toggle(label='On/Off', active = True)
on_chb.on_click( update_on_chb)

scale_chb    = Dropdown(label="Scale B", menu = escV, disabled = False )
scale_chb.on_change('value',update_scale_chb)

dc_coupling_chb = Toggle(label="Coupling: DC", active = True)
dc_coupling_chb.on_click(update_dc_coupling_chb)

chb_layout = channel_layout(text_chb,on_chb, dc_coupling_chb, scale_chb)

######## TRIGGER #########

NUM_SAMPLES= 300
text_trigger    = Div(text='<hr><h2>Trigger</h2>')

trigger_run = Toggle(label="Run", active=True)
trigger_run.on_click(update_trigger_run)
app.set_change_status_callback(update_status)#, trigger_run)

trigger_type    = Dropdown(label="Type", menu = trig_types, disabled = False )
trigger_type.on_change('value',update_trigger_type)

trigger_source = Toggle(label="Source", active=True)
trigger_source.on_click(update_trigger_source)

trigger_edge = Toggle(label="Edge", active=True)
trigger_edge.on_click(update_trigger_edge)

pre_trigger = Slider(title="Pretrigger", value=150, start=0, end=NUM_SAMPLES, step=1, callback_policy='mouseup')
pre_trigger.on_change('value',update_pre_trigger)

trigger = Slider(title="Trigger", value=150, start=0, end=NUM_SAMPLES, step=1, callback_policy='mouseup')
trigger.on_change('value',update_trigger_val)

tri_layout = trigger_layout(text_trigger,trigger_run,trigger_type,trigger_source, trigger_edge,pre_trigger,trigger)

######### Time ###########

text_horiz = Div(text='<hr><h2>Horizontal</h2>')
horizontal  = Dropdown(label="Base de Tiempo", menu=escT, disabled= False)
horizontal.on_change('value',update_horizontal)

hor_layout = column([text_horiz,horizontal],sizing_mode=MODE)


######### Layout ############

sliders = column([ connect_layout,cha_layout, chb_layout, tri_layout, hor_layout,Div(text='<hr>') ],
                 sizing_mode=MODE )
rightPanel = column([ plot, Div(text= AUTORS)], sizing_mode=MODE )
doc.add_root( row( sliders, rightPanel, sizing_mode=MODE ) )
doc.title = "Smartbench"











# plot.xaxis[0].ticker=FixedTicker(ticks=np.arange(-15,200,5))   #spacing by 5 units from -15 to 200
# plot.xgrid[0].ticker=FixedTicker(ticks=np.arange(-15,200,5))
# #change yaxis ticker & ygrid ticker with fixed-width spacing
# plot.yaxis[0].ticker=FixedTicker(ticks=np.arange(0,101,5))   #spacing by 5 units from 0 to 100
# plot.ygrid[0].ticker=FixedTicker(ticks=np.arange(0,101,5))
#plot.xaxis.bounds = (0, 99)
# plot.yaxis.bounds = (0, 255)
# p.xaxis.ticker = FixedTicker(ticks=[10, 20, 37.4])
# p.xaxis.major_tick_line_color = "firebrick"
# p.xaxis.major_tick_line_width = 3
# p.xaxis.minor_tick_line_color = "orange"
# p.yaxis.minor_tick_line_color = None
# p.axis.major_tick_out = 10
# p.axis.minor_tick_in = -3
# p.axis.minor_tick_out = 8

# Set up widgets

#
#listScaleV.value = escV[0][1]
#listScaleT.value = escT[0][1]
#listScaleV.label = escV[int(listScaleV.value)][0]
#listScaleT.label = escT[int(listScaleT.value)][0]
#
#
#myApp = SmartbenchApp(doc, plot, source_chA, source_chB)

#
#def updateStatus(attrname):
#    global myApp
#    if(tglStart.active == True):
#        tglStart.label = "Stop"
#        #myApp.smartbench.set_trigger_mode_auto()
#        myApp.start()
#    else:
#        myApp.stop()
#        tglStart.label = "Start"
#    return
#
#def updateScaleV(attrname):
#    listScaleV.label = escV[int(listScaleV.value)][0]
#    #myApp.smartbench.
#    return
#
#def updateScaleT(attrname):
#    listScaleT.label = escV[int(listScaleT.value)][0]
#    #...
#    return
#
#def update_DC_coupling_cha(attrname):
#    print("attrname={}".format(attrname))
#    if(DC_coupling_cha.active==True):
#        DC_coupling_cha.label = "Coupling: DC"
#        myApp.smartbench.chA.set_coupling_dc()
#        myApp.smartbench.chA.send_settings()
#    else:
#        myApp.smartbench.chA.set_coupling_ac()
#        myApp.smartbench.chA.send_settings()
#        DC_coupling_cha.label ="Coupling: AC"
#    return
#
#def update_att_cha(attrname, old, new):
#    myApp.smartbench.chA.set_attenuator(att_cha.value)
#    myApp.smartbench.chA.send_settings()
#    return
#
#def update_gain_cha(attrname, old, new):
#    myApp.smartbench.chA.set_gain(gain_cha.value)
#    myApp.smartbench.chA.send_settings()
#    return
#
#def update_offset_cha(attrname, old, new):
#    #print("old,new = {},{}".format(old, new))
#    #myApp.smartbench.chA.set_offset(int(offset_cha.value))
#    return
#
#
#def update_DC_coupling_chb(attrname):
#    #print("attrname={}".format(attrname))
#    if(DC_coupling_chb.active==True):
#        myApp.smartbench.chB.set_coupling_dc()
#        DC_coupling_chb.label = "Coupling: DC"
#        myApp.smartbench.chB.send_settings()
#    else:
#        myApp.smartbench.chB.set_coupling_ac()
#        DC_coupling_chb.label ="Coupling: AC"
#        myApp.smartbench.chB.send_settings()
#    return
#
#def update_att_chb(attrname, old, new):
#    myApp.smartbench.chB.set_attenuator(att_chb.value)
#    myApp.smartbench.chB.send_settings()
#    return
#
#def update_gain_chb(attrname, old, new):
#    myApp.smartbench.chB.set_gain(gain_chb.value)
#    myApp.smartbench.chB.send_settings()
#    return
#
#def update_offset_chb(attrname, old, new):
#    #myApp.smartbench.chB.set_offset(offset_chb.value)
#    return
#
#
#def update_mov_ave(attrname, old, new):
#    myApp.smartbench.chA.set_nprom(2**mov_ave.value)
#    myApp.smartbench.chB.set_nprom(2**mov_ave.value)
#    return
#
#def update_adc_clk_div(attrname, old, new):
#    myApp.smartbench.set_clk_divisor(int(adc_clk_div.value))
#    myApp.smartbench.set_clk_divisor(int(adc_clk_div.value))
#    return
#
#def update_trigger_val(attrname, old, new):
#    myApp.smartbench.set_trigger_value(trigger_val.value)
#    return
#
#def update_num_samples(attrname, old, new):
#    myApp.smartbench.set_number_of_samples(num_samples.value)
#    if(pre_trigger.value > num_samples.value):
#        pre_trigger.value = num_samples.value
#    pre_trigger.end = num_samples.value
#    return
#
#def update_pre_trigger(attrname, old, new):
#    myApp.smartbench.set_pretrigger(pre_trigger.value)
#    return
#
##text.on_change('value', update_title)
#
## Callbacks associations
#tglStart.on_click(updateStatus)
#listScaleV.on_click(updateScaleV)
#listScaleT.on_click(updateScaleT)
#
#DC_coupling_cha.on_click(update_DC_coupling_cha)
#att_cha.on_change('value',update_att_cha)
#gain_cha.on_change('value',update_gain_cha)
#offset_cha.on_change('value',update_offset_cha)
#
#DC_coupling_chb.on_click(update_DC_coupling_chb)
#att_chb.on_change('value',update_att_chb)
#gain_chb.on_change('value',update_gain_chb)
#offset_chb.on_change('value',update_offset_chb)
#
#mov_ave.on_change('value',update_mov_ave)
#adc_clk_div.on_change('value',update_adc_clk_div)
#
#trigger_val.on_change('value', update_trigger_val)
#num_samples.on_change('value', update_num_samples)
#pre_trigger.on_change('value', update_pre_trigger)
#
#
## Initialization of sliders, buttons, etc
#DC_coupling_cha.active = bool(myApp.smartbench.chA.get_coupling())
#att_cha.value       = myApp.smartbench.chA.get_attenuator()
#gain_cha.value      = myApp.smartbench.chA.get_gain()
#offset_cha.value    = str(myApp.smartbench.chA.get_offset())
#
#DC_coupling_chb.active = bool(myApp.smartbench.chB.get_coupling())
#att_chb.value       = myApp.smartbench.chB.get_attenuator()
#gain_chb.value      = myApp.smartbench.chB.get_gain()
#offset_chb.value    = myApp.smartbench.chB.get_offset()
#
#mov_ave.value   = int(log(myApp.smartbench.chA.get_nprom(),2))
#adc_clk_div.value   =str(myApp.smartbench.chA.get_clk_divisor())
#
#trigger_val.value   = myApp.smartbench.get_trigger_value()
#num_samples.value   = myApp.smartbench.get_number_of_samples()
#pre_trigger.value  = myApp.smartbench.get_pretrigger()
#
##if(DC_coupling_cha.active==True):
#    #DC_coupling_cha.label = "Coupling: DC"
#
## https://bokeh.pydata.org/en/latest/docs/reference/models/layouts.html#bokeh.models.layouts.LayoutDOM
