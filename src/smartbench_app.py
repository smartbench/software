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

from math import sin,pi

from pyftdi.ftdi import Ftdi
import time



x = range(0,500)
y = [ sin(2*pi*i/500.) for i in range(0,500) ]

fig, ax = plt.subplots()
ax.plot( x, y, 'r-' , label='y=sin(x)' )
ax.set_ylabel('y')
ax.set_title('A beautiful sinewave function')
ax.set_xlabel('x')
ax.legend( loc='upper right', shadow=True )

canvas= fig.canvas
nav = NavigationToolbar2Kivy(canvas)

baseText = ("Run it again?","Press me to \nstop the \nsinewave")

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
    ft = Ftdi()

    def __init__( self, **kwargs):
        super( rightPanel, self).__init__()
        self.ids.kn._value(self.ids.kn,self.ids.kn.value)
        dev_list = self.ft.find_all([(0x0403,0x6010)],True)
        if(len(dev_list) > 0):
            print ("Device found:\n\t", dev_list)
            self.ft.open(vendor=0x0403,product=0x6010,interface=2)
            print("Opened device!")
        else:
            print ("Device not connected!")
            exit()
        self.state = 1
        self.k = 0
        self.i = 1

    def btOpCallback(self):
        if self.state:
            self.state=0
            Clock.unschedule(self.myCallback)
            self.btText = baseText[0]
        else:
            self.state=1
            Clock.schedule_interval(self.myCallback,0.1)
            self.btText = baseText[1]

    def myCallback( self, dt ):
        self.k = self.k + 10
        y = [ (self.ids.kn.value*(sin(2*pi*(i-self.k)/500.))) for i in range(0,500) ]
        ax.clear()
        ax.plot( x, y, 'r-' , label='y=sin(x)' )
        canvas.draw()
        self.i = ( self.i*2 )%255
        print( self.ft.write_data(bytes( [ self.i ] ) ), self.i )
        time.sleep(0.5)



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
    rp = rightPanel()

    def __init__(self,**kwargs):
        super(MainWindow, self).__init__()
        self.ids.leftPanel.add_widget(nav.actionbar)
        self.ids.leftPanel.add_widget(canvas)
        self.add_widget(self.rp)
        Clock.schedule_interval(self.rp.myCallback,0.1)

class SmartbenchApp(App):
    title = 'SmartbenchApp'
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    SmartbenchApp().run()
