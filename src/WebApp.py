'''
To run the server

    bokeh serve WebApp.py

Then navigate to the URL

    http://localhost:5006/WebApp

in your browser.

'''
import numpy as np

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
plot = figure(plot_width= 100, plot_height= 100,sizing_mode='scale_both',title="Signal",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

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
text        = TextInput(title="title", value='Signal')
offset      = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude   = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase       = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq        = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)
spa         = Spacer(sizing_mode= 'stretch_both')
#btnStart = Button(label="Start", button_type=)
tglStart    = Toggle(label="Start", active=False, width=130)
listScaleV  = Dropdown(label="Escala V", menu=escV, width=130)
listScaleT  = Dropdown(label="Base de Tiempo", menu=escT, width=130)
spa2        = Spacer(sizing_mode= 'stretch_both')

listScaleV.value = escV[0][1]
listScaleT.value = escT[0][1]
listScaleV.label = escV[int(listScaleV.value)][0]
listScaleT.label = escT[int(listScaleT.value)][0]


myApp = SmartbenchApp(doc, plot, source_chA, source_chB)

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    x = np.linspace(0, 4*np.pi, N)
    y_sin = a*np.sin(k*x + w) + b
    y_cos = a*np.cos(k*x + w) + b

    source_chA.data = dict(x=x, y=y_sin)
    source_chB.data = dict(x=x, y=y_cos)

for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)

def updateStatus(attrname):
    global myApp
    if(tglStart.active == True):
        tglStart.label = "Stop"
        myApp.start()
    else:
        myApp.stop()
        tglStart.label = "Start"
    return

tglStart.on_click(updateStatus)

def updateScaleV(attrname):
    listScaleV.label = escV[int(listScaleV.value)][0]
    #myApp.smartbench.
    return

listScaleV.on_click(updateScaleV)

def updateScaleT(attrname):
    listScaleT.label = escV[int(listScaleT.value)][0]

    return

listScaleT.on_click(updateScaleT)



# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq, tglStart, listScaleV, listScaleT, sizing_mode='stretch_both')

doc.add_root(row(inputs,plot,sizing_mode= 'stretch_both'))
doc.title = "Smartbench"
