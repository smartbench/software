''' Present an interactive function explorer with slider widgets.

Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.

Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve WebApp.py

at your command prompt. Then navigate to the URL

    http://localhost:5006/WebApp

in your browser.

'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.layouts import Spacer
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure

# From here, handle the FTDI:
from OscopeApi import *
#from SmartbenchApp import *

from tornado import gen
import tornado


# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))
doc = curdoc()


# Set up plot
plot = figure(plot_width= 100, plot_height= 100,sizing_mode='scale_both',title="Signal",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)


# Set up widgets
text = TextInput(title="title", value='Signal')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)
spa = Spacer(sizing_mode= 'stretch_both')
spa2 = Spacer(sizing_mode= 'stretch_both')


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
    y = a*np.sin(k*x + w) + b

    source.data = dict(x=x, y=y)

for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq,sizing_mode='stretch_both')

i = 0

#####################
# TEST CALLBACK
# @gen.coroutine
# def periodic_callback():
#     global i,x,y,text,source,doc
#     i = i + 1
#     text.value = "ALALA"
#     print("i={}   {}".format(i, "!"))
#     x = np.linspace(0, 4*np.pi, N)
#     y = y+y
#     source.data = dict(x=x, y=y)
#     yield tornado.gen.sleep(1)
#     print("wololo")
#     doc.add_next_tick_callback(periodic_callback)
#     #doc.add_timeout_callback(periodic_callback, 1000)
#     return
#
# print("> START")
# text.value = "LLL"
# doc.add_next_tick_callback(periodic_callback)
#doc.add_timeout_callback(periodic_callback, 1)
########################
# https://bokeh.pydata.org/en/latest/docs/reference/server/callbacks.html
# https://bokeh.pydata.org/en/latest/docs/reference/document.html#bokeh.document.document.Document


class SmartbenchApp():
    global source,doc, plot

    def __init__(self,**kwargs):
        self.smartbench = Smartbench()
        self.smartbench.setDefaultConfiguration()
        self.dataX = np.linspace(0, 4*np.pi, 200)
        self.dataY = np.cos(self.dataX)*np.cos(self.dataX)
        source.data = dict(x=self.dataX, y=self.dataY)
        print(">>><<<")
        doc.add_next_tick_callback(self.newFrameCallback)

    # --------------------------------------------------------
    # This method sends a "Start Request" to the device.
    @gen.coroutine
    def newFrameCallback(self):
        self.triggered      = 0
        self.buffer_full    = 0
        self.count          = 0
        print("> Request Start")
        self.smartbench.request_start()
        doc.add_next_tick_callback(self.waitingTriggerCallback) # Called as soon as possible
        return

    # --------------------------------------------------------
    # This method will query the trigger status and the buffer status, which could
    # be {Triggered / Not triggered} and { buffer full / buffer not full } respectively.
    # Depending on the status, and the mode of operation (Normal or Auto) will wait or
    # not to show the data.
    @gen.coroutine
    def waitingTriggerCallback(self):
        print("> Request Trigger Status")
        self.smartbench.request_trigger_status()
        print("> Waiting...")
        self.buffer_full,self.triggered = self.smartbench.receive_trigger_status()
        print("> Trigger={}\tBuffer_full={}".format( self.triggered, self.buffer_full ))

        if self.triggered==0 or self.buffer_full==0:
            if( self.smartbench.is_trigger_mode_single() or self.smartbench.is_trigger_mode_normal() ):
                doc.add_timeout_callback(self.waitingTriggerCallback,0.5) # Check again in 500 ms.
                return
            else:
                if(self.buffer_full == 1 and self.count < 5):
                    self.count = self.count + 1
                    Clock.schedule_once(self.waitingTriggerCallback,0.5) # Check again in 500 ms.
                    return

        # First, stops the capturing.
        print("> Request Stop")
        self.smartbench.request_stop()

        # Then, requests the data.
        print("> Request CHA")
        self.smartbench.request_chA()

        print("> Waiting...")
        self.dataY = list(reversed(self.smartbench.receive_channel_data()))
        self.dataX = range(0,len(self.dataY))
        plot.x_range = Range1d(min(self.dataX), max(self.dataX))
        plot.y_range = Range1d(min(self.dataY), max(self.dataY))
        #self.mw.updatePlot( self.dataX, self.dataY )
        #self.mw.plotTriggerPoint( self.smartbench.get_pretrigger()-1, self.smartbench.get_trigger_value() )
        source.data = dict(x=self.dataX, y=self.dataY)

        if( self.smartbench.is_trigger_mode_auto() or self.smartbench.is_trigger_mode_normal() ):
            doc.add_next_tick_callback(self.newFrameCallback ) # Called as soon as possible

        return

myApp = SmartbenchApp()

doc.add_root(row(inputs,plot,sizing_mode= 'stretch_both'))
doc.title = "Smartbench"
