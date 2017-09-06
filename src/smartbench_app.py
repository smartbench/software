""" Smartbench app

This app is the computer-side part of Smartbench project.
You can control the scope, see the measured signal and do some post-processing.

Authors:
            IP      Ivan Santiago Paunovic


Version:
            Date            Number          Name            Modified by     Comment
            2017/07/17      0.1             SmBegins_mplf   IP              First approach. Using garden.matplotlib.
            2017/07/19      0.1             SmBegins_mplf   IP              Working. First layout. Added a button, knob and a plot.
                                                                            Plot is updated periodically.
            2017/07/20      0.1             SmBegins_mplf   IP              Added an action when button is pressed. Using the knob value
                                                                            (in progress)

ToDo:
            Date            Suggested by    Activity                Description
            2017/07/17      IP              Try garden.graph        Create another branch using garden.graph instead of garden.matplotlib.

Releases:   In development ...
"""
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from kivy.garden.matplotlib.backend_kivy import FigureCanvasKivy,\
                                                                NavigationToolbar2Kivy

from kivy.clock import Clock

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.actionbar import ActionBar
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

from kivy.garden.knob import Knob

# from kivy.garden.graph import Graph, MeshLinePlot

from math import sin,pi

import kivy # require
#from pyftdi.ftdi import Ftdi
import serial
import time

from smartbench_api import *

x = range(0,500)
#y = [ sin(2*pi*i/500.) for i in range(0,500) ]
y = [i for i in range(500)]

fig, ax = plt.subplots()
ax.plot( x, y, 'r-' , label='y=sin(x)' )
ax.set_ylabel('y')
ax.set_title('A beautiful sinewave function')
ax.set_xlabel('x')
ax.legend( loc='upper right', shadow=True )

canvas= fig.canvas
nav = NavigationToolbar2Kivy(canvas)

baseText = ("Run it again?","Press me to \nstop the \nsinewave")

#b = BoxLayout(orientation='vertical')
# graph = Graph(xlabel='X', ylabel='Y', x_ticks_minor=5,
#     x_ticks_major=25, y_ticks_major=1,
#     y_grid_label=True, x_grid_label=True, padding=5,
#     x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=0, ymax=255)
# plot = MeshLinePlot(color=[1, 0, 0, 1])
# plot.points = [(i, sin(i / 10.)) for i in range(0, 100)]
# graph.add_plot(plot)
#b.add_widget(graph)
#self.plot = plot

Builder.load_string( '''
<rightPanel>:
    size_hint: .15,1
    orientation: 'vertical'
    spacing: 10
    Knob:
        id: kn
        value: .5
        min: 0.0
        step: 0.1
        max: 1.0
        curve: 1                                # A mayor valor mayor sensibilidad. curve=1 es lineal.
        knobimg_source: "img/knob_black.png"
        markeroff_color: 0.0, 0.0, .0, 1
        knobimg_size: 0.9
        marker_img: "img/bline3.png"
        show_marker: False
    #    on_touch_down: root.my_on_touch_down
    #    on_touch_move: root.my_on_touch_move
    Label:
        text: "Hola mundo"
    Button:
        on_press: root.btOpCallback()
        # id: btPressMe
        # text: "Press me, bitch"
        text: root.btText
''')

class rightPanel(BoxLayout):
    btText = StringProperty(baseText[1])
    state = 1
    k = 0

    def __init__( self, smartbench, **kwargs):
        super( rightPanel, self).__init__()
        self.ids.kn._value(self.ids.kn,self.ids.kn.value)
        self.smartbench = smartbench

    def btOpCallback(self):
        if self.state:
            self.state=0
            Clock.unschedule(self.myCallback)
            self.btText = baseText[0]
        else:
            self.state=1
            Clock.schedule_interval(self.myCallback,0.1)
            self.btText = baseText[1]

    def myCallback(self,dt):
        self.k = self.k + 10
        # y = [ (self.ids.kn.value*(sin(2*pi*(i-self.k)/500.))) for i in range(0,500) ]
        # ax.clear()
        # ax.plot( x, y, 'r-' , label='y=sin(x)' )
        # canvas.draw()
        triggered = 0
        buffer_full = 0
        print("> Request Start")
        self.smartbench.request_start()
        print("> Request Trigger Status")
        self.smartbench.request_trigger_status()
        print("> Waiting...")
        buffer_full,triggered = self.smartbench.receive_trigger_status()
        print("> Trigger={}\tBuffer_full={}".format(triggered,buffer_full))
        while triggered==0 or buffer_full==0:
            time.sleep(0.5)
            print("> Request Trigger Status")
            self.smartbench.request_trigger_status()
            print("> Waiting...")
            buffer_full,triggered = self.smartbench.receive_trigger_status()
            print("> Trigger={}\tBuffer_full={}".format(triggered,buffer_full))
        print("> Request Stop")
        self.smartbench.request_stop()
        print("> Request CHA")
        self.smartbench.request_chA()
        print("> Waiting...")
        self.dataY = list(reversed(self.smartbench.receive_channel_data()))
        self.dataX = range(0,len(self.dataY))

        ax.clear()
        ax.plot( self.dataX, self.dataY, 'r-' , label='Smartbench' )
        ax.plot( self.smartbench.get_pretrigger()-1, self.smartbench.get_trigger_value(), 'b*')
        canvas.draw()

    #def plotData(self, x, y):
    #    ax.clear()
    #    ax.plot( x, y, 'r-' , label='y=sin(x)' )
    #    canvas.draw()


Builder.load_string( '''
<MainWindow>:
    orientation: 'horizontal'                                               # 'vertical'
    spacing: 10                                                             # in pixels
    BoxLayout:
        id: leftPanel
        orientation: 'vertical'
        spacing: 10
''')

class MainWindow(BoxLayout):
    #myScope = _Oscope_ftdi()
    #rp = rightPanel()

    def __init__(self,**kwargs):
        #If a user attempts to run your application with a version of Kivy that is older than the specified version, an Exception is raised
        kivy.require('1.0.1')
        self.smartbench = Smartbench()
        self.rp = rightPanel(self.smartbench)

        super(MainWindow, self).__init__()
        self.ids.leftPanel.add_widget(nav.actionbar)
        self.ids.leftPanel.add_widget(canvas)
        self.add_widget(self.rp)
        Clock.schedule_interval(self.rp.myCallback,0.1)

        #MainWindow.smartbench.open()
        self.smartbench.set_trigger_source_cha()
        self.smartbench.set_trigger_negedge()
        self.smartbench.set_trigger_value(-28)
        self.smartbench.set_number_of_samples(150)
        self.smartbench.set_pretrigger(50)
        self.smartbench.send_trigger_settings()

        self.smartbench.chA.set_attenuator(1)
        self.smartbench.chA.set_gain(2)
        self.smartbench.chA.set_coupling_dc()
        self.smartbench.chA.set_ch_on()
        self.smartbench.chA.send_settings()
        self.smartbench.chA.set_offset(0)
        self.smartbench.chA.set_nprom(1)
        self.smartbench.chA.set_clk_divisor(1)

        self.smartbench.chB.set_attenuator(3)
        self.smartbench.chB.set_gain(4)
        self.smartbench.chB.set_coupling_dc()
        self.smartbench.chB.set_ch_on()
        self.smartbench.chB.send_settings()
        self.smartbench.chB.set_offset(0)
        self.smartbench.chB.set_nprom(1)
        self.smartbench.chB.set_clk_divisor(1)

        return

class SmartbenchApp(App):
    title = 'SmartbenchApp'
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    try:
        SmartbenchApp().run()
    except KeyboardInterrupt:
        print ("Interrupted")
        MainWindow.smartbench.oscope.close()
        exit()
