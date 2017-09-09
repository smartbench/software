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
    state = 1
    k = 0

    def __init__( self, **kwargs):
        super( rightPanel, self).__init__()
        self.ids.kn._value(self.ids.kn,self.ids.kn.value)

    def btOpCallback(self):
        return
    #     if self.state:
    #         self.state=0
    #         Clock.unschedule(self.myCallback)
    #         self.btText = baseText[0]
    #     else:
    #         self.state=1
    #         Clock.schedule_interval(self.myCallback,0.1)
    #         self.btText = baseText[1]

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

    def __init__(self,**kwargs):
        #If a user attempts to run your application with a version of Kivy that is older than the specified version, an Exception is raised
        kivy.require('1.0.1')

        self.fig, self.ax = plt.subplots()
        self.ax.plot( x, y, 'r-' , label='y=sin(x)' )
        self.ax.set_ylabel('y')
        self.ax.set_title('A beautiful sinewave function')
        self.ax.set_xlabel('x')
        self.ax.legend( loc='upper right', shadow=True )

        self.canvas= fig.canvas
        self.nav = NavigationToolbar2Kivy(canvas)

        self.rp = rightPanel(self.smartbench)
        self.add_widget(self.rp)

        super(MainWindow, self).__init__()
        return
