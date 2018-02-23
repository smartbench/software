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
from math import log

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.layouts import Spacer
from bokeh.models.widgets import Slider, TextInput, Button, Toggle, Dropdown
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure
from bokeh.palettes import Viridis3

from tornado import gen
import tornado

from OscopeApi import *
from Configuration_Definitions import *
from SmartbenchApp import SmartbenchApp


_STATUS_STOPPED = 0
_STATUS_RUNNING = 1

_CHANNEL_ON     = 1
_CHANNEL_OFF    = 0

MODE='scale_width'
DEFAULT_WIDTH = 300

# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y_sin = np.sin(x)
y_cos = np.cos(x)
source_chA = ColumnDataSource(data=dict(x=x, y=y_sin))
source_chB = ColumnDataSource(data=dict(x=x, y=y_cos))
doc = curdoc()

escV = [(str(x),str(i)) for i,x in enumerate(Configuration_Definitions.voltage_scales_str)]
escT = [(str(x),str(i)) for i,x in enumerate(Configuration_Definitions.timebase_scales_str)]


# Set up plot
plot = figure(plot_width= 10,
              plot_height= 10,
              sizing_mode='scale_both',
              title="Signal",
              tools="",#tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi],
              y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source_chA, line_width=3, line_alpha=0.6, color=Viridis3[0], legend="Channel A")
plot.line('x', 'y', source=source_chB, line_width=3, line_alpha=0.6, color=Viridis3[1], legend="Channel B")

# https://bokeh.pydata.org/en/latest/docs/user_guide/styling.html
#legend, grid, xgrid, ygrid, axis, xaxis, yaxis
plot.legend.location = "top_right"
plot.xaxis.axis_label = "Tiempo []"
plot.yaxis.axis_label = "Tensión []"

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
text_cha    = TextInput(title="",
                        value='Channel A',
                        disabled=True)

# offset_cha  = Slider(title="Offset",
#                      value=0,
#                      start=-512,
#                      end=511,
#                      step=1,
#                      callback_policy='mouseup') #to avoid multiple writes

offset_cha    = TextInput(title="Offset CHA <-521,+511>",
                        value='0',
                        disabled=True)

gain_cha    = Slider(title="Gain",
                     value=0,
                     start=0,
                     end=7,
                     step=1,
                     callback_policy='mouseup')

att_cha     = Slider(title="Attenuation",
                     value=0,
                     start=0,
                     end=7,
                     step=1,
                     callback_policy='mouseup')


DC_coupling_cha = Toggle(label="Coupling: DC",
                     active=False)


text_chb    = TextInput(title="",
                        value='Channel B',
                        disabled=True)

offset_chb  = Slider(title="Offset",
                     value=0,
                     start=-512,
                     end=511,
                     step=1,
                     disabled=True,
                     callback_policy='mouseup') #to avoid multiple writes

gain_chb    = Slider(title="Gain",
                     value=0,
                     start=0,
                     end=7,
                     step=1,
                     callback_policy='mouseup')

att_chb     = Slider(title="Attenuation",
                     value=0,
                     start=0,
                     end=7,
                     step=1,
                     callback_policy='mouseup')

DC_coupling_chb = Toggle(label="Coupling: DC",
                     active=False)


# Both channels

mov_ave     = Slider(title="Moving Average [N=2^k] (CHA) k",
                     value=0,
                     start=0,
                     end=3,
                     step=1,
                     callback_policy='mouseup')

# adc_clk_div = Slider(title="ADC Clock divisor /* 32 bits */",
#                      value=0,
#                      start=5,
#                      end=2**32,
#                      step=1)
adc_clk_div = TextInput(title="ADC Clock divisor (32 bits)",
                        value='5')

tglStart    = Toggle(label="Start",
                     active=False)

listScaleV  = Dropdown(label="Escala V",
                       menu=escV,
                       disabled=True)

listScaleT  = Dropdown(label="Base de Tiempo",
                       menu=escT,
                       disabled=True)

trigger_val = Slider(title="Trigger Value",
                     value=-28,
                     start=-128,
                     end=127,
                     step=1,
                     callback_policy='mouseup')

num_samples = Slider(title="Number of samples",
                     value=150,
                     start=50,
                     end=1000, # <-- Check max (depends on available ram)
                     step=1,
                     callback_policy='mouseup')

pre_trigger = Slider(title="Pretrigger",
                     value=150,
                     start=0,
                     end=num_samples.value,
                     step=1,
                     callback_policy='mouseup')

# To add:
# Trigger source (cha, chb, ext)
# Trigger edge (pos, neg)
# Trigger mode (single, normal, auto)
# chA on/off
# chB on/off

# Timebase
# V/div (both channels)



listScaleV.value = escV[0][1]
listScaleT.value = escT[0][1]
listScaleV.label = escV[int(listScaleV.value)][0]
listScaleT.label = escT[int(listScaleT.value)][0]


myApp = SmartbenchApp(doc, plot, source_chA, source_chB)

# Set up callbacks
# def update_title(attrname, old, new):
#     plot.title.text = text.value
#
# text.on_change('value', update_title)

def updateStatus(attrname):
    global myApp
    if(tglStart.active == True):
        tglStart.label = "Stop"
        myApp.start()
    else:
        myApp.stop()
        tglStart.label = "Start"
    return

def updateScaleV(attrname):
    listScaleV.label = escV[int(listScaleV.value)][0]
    #myApp.smartbench.
    return

def updateScaleT(attrname):
    listScaleT.label = escV[int(listScaleT.value)][0]
    #...
    return

def update_DC_coupling_cha(attrname):
    print("attrname={}".format(attrname))
    if(DC_coupling_cha.active==True):
        myApp.smartbench.chA.set_coupling_dc()
        DC_coupling_cha.label = "Coupling: DC"
        myApp.smartbench.chA.send_settings()
    else:
        myApp.smartbench.chA.set_coupling_ac()
        DC_coupling_cha.label ="Coupling: AC"
        myApp.smartbench.chA.send_settings()
    return

def update_att_cha(attrname, old, new):
    myApp.smartbench.chA.set_attenuator(att_cha.value)
    myApp.smartbench.chA.send_settings()
    return

def update_gain_cha(attrname, old, new):
    myApp.smartbench.chA.set_gain(gain_cha.value)
    myApp.smartbench.chA.send_settings()
    return

def update_offset_cha(attrname, old, new):
    #print("old,new = {},{}".format(old, new))
    #myApp.smartbench.chA.set_offset(int(offset_cha.value))
    return


def update_DC_coupling_chb(attrname):
    #print("attrname={}".format(attrname))
    if(DC_coupling_chb.active==True):
        myApp.smartbench.chB.set_coupling_dc()
        DC_coupling_chb.label = "Coupling: DC"
        myApp.smartbench.chB.send_settings()
    else:
        myApp.smartbench.chB.set_coupling_ac()
        DC_coupling_chb.label ="Coupling: AC"
        myApp.smartbench.chB.send_settings()
    return

def update_att_chb(attrname, old, new):
    myApp.smartbench.chB.set_attenuator(att_chb.value)
    myApp.smartbench.chB.send_settings()
    return

def update_gain_chb(attrname, old, new):
    myApp.smartbench.chB.set_gain(gain_chb.value)
    myApp.smartbench.chB.send_settings()
    return

def update_offset_chb(attrname, old, new):
    #myApp.smartbench.chB.set_offset(offset_chb.value)
    return


def update_mov_ave(attrname, old, new):
    myApp.smartbench.chA.set_nprom(2**mov_ave.value)
    myApp.smartbench.chB.set_nprom(2**mov_ave.value)
    return

def update_adc_clk_div(attrname, old, new):
    myApp.smartbench.chA.set_clk_divisor(int(adc_clk_div.value))
    myApp.smartbench.chB.set_clk_divisor(int(adc_clk_div.value))
    return

def update_trigger_val(attrname, old, new):
    myApp.smartbench.set_trigger_value(trigger_val.value)
    return

def update_num_samples(attrname, old, new):
    myApp.smartbench.set_number_of_samples(num_samples.value)
    if(pre_trigger.value > num_samples.value):
        pre_trigger.value = num_samples.value
    pre_trigger.end = num_samples.value
    return

def update_pre_trigger(attrname, old, new):
    myApp.smartbench.set_pretrigger(pre_trigger.value)
    return

#text.on_change('value', update_title)

# Callbacks associations
tglStart.on_click(updateStatus)
listScaleV.on_click(updateScaleV)
listScaleT.on_click(updateScaleT)

DC_coupling_cha.on_click(update_DC_coupling_cha)
att_cha.on_change('value',update_att_cha)
gain_cha.on_change('value',update_gain_cha)
offset_cha.on_change('value',update_offset_cha)

DC_coupling_chb.on_click(update_DC_coupling_chb)
att_chb.on_change('value',update_att_chb)
gain_chb.on_change('value',update_gain_chb)
offset_chb.on_change('value',update_offset_chb)

mov_ave.on_change('value',update_mov_ave)
adc_clk_div.on_change('value',update_adc_clk_div)

trigger_val.on_change('value', update_trigger_val)
num_samples.on_change('value', update_num_samples)
pre_trigger.on_change('value', update_pre_trigger)


# Initialization of sliders, buttons, etc
DC_coupling_cha.active = bool(myApp.smartbench.chA.get_coupling())
att_cha.value       = myApp.smartbench.chA.get_attenuator()
gain_cha.value      = myApp.smartbench.chA.get_gain()
offset_cha.value    = str(myApp.smartbench.chA.get_offset())

DC_coupling_chb.active = bool(myApp.smartbench.chB.get_coupling())
att_chb.value       = myApp.smartbench.chB.get_attenuator()
gain_chb.value      = myApp.smartbench.chB.get_gain()
offset_chb.value    = myApp.smartbench.chB.get_offset()

mov_ave.value   = int(log(myApp.smartbench.chA.get_nprom(),2))
adc_clk_div.value   =str(myApp.smartbench.chA.get_clk_divisor())

trigger_val.value   = myApp.smartbench.get_trigger_value()
num_samples.value   = myApp.smartbench.get_number_of_samples()
pre_trigger.value  = myApp.smartbench.get_pretrigger()

#if(DC_coupling_cha.active==True):
    #DC_coupling_cha.label = "Coupling: DC"

# https://bokeh.pydata.org/en/latest/docs/reference/models/layouts.html#bokeh.models.layouts.LayoutDOM
# usar siempre "scale_width"

command = row([tglStart, listScaleV, listScaleT],
              sizing_mode=MODE,
              width=DEFAULT_WIDTH )

#sliders = column([text, offset, amplitude, phase, freq, command],
                 #sizing_mode=MODE )
sliders = column([ command,
                  text_cha,
                  DC_coupling_cha,
                  att_cha,
                  gain_cha,
                  offset_cha,
                  text_chb,
                  DC_coupling_chb,
                  att_chb,
                  gain_chb,
                  offset_chb,
                  mov_ave,
                  adc_clk_div,
                  trigger_val,
                  num_samples,
                  pre_trigger
                  ],
                 sizing_mode=MODE )

rightPanel = column([ plot],
                    sizing_mode=MODE )


doc.add_root( row(
                sliders,
                rightPanel,
                sizing_mode=MODE ) )

doc.title = "Smartbench"
