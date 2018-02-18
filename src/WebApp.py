'''
To run the server

    bokeh serve WebApp.py

Then navigate to the URL

    http://localhost:5006/WebApp

in your browser.

'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.layouts import Spacer
from bokeh.models.widgets import Slider, TextInput, Button, Toggle
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


# Set up plot
plot = figure(plot_width= 100, plot_height= 100,sizing_mode='scale_both',title="Signal",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source_chA, line_width=3, line_alpha=0.6, color=Viridis3[0])
plot.line('x', 'y', source=source_chB, line_width=3, line_alpha=0.6, color=Viridis3[1])


# Set up widgets
text = TextInput(title="title", value='Signal')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)
#btnStart = Button(label="Start", button_type=)
tglStart = Toggle(label="Start/Stop", active=False)
spa = Spacer(sizing_mode= 'stretch_both')
spa2 = Spacer(sizing_mode= 'stretch_both')


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
        myApp.start()
    else:
        myApp.stop()
    return

tglStart.on_click(updateStatus)

# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq, tglStart, sizing_mode='stretch_both')

doc.add_root(row(inputs,plot,sizing_mode= 'stretch_both'))
doc.title = "Smartbench"
