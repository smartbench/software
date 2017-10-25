""" Layout of Smartbench app and basic actions """

# Matplotlib includes
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Kivy includes
import kivy # require
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

class MainWindow(BoxLayout):

    def __init__(self,**kwargs):
        #If a user attempts to run your application with a version of Kivy that is older than the specified version, an Exception is raised
        kivy.require('1.0.1')

        self.rp = rightPanel()
        super(MainWindow, self).__init__()

        # # Creting plot
        x = range(0,500)
        y = [i for i in range(500)]
        self.fig, self.ax = plt.subplots()
        self.ax.plot( x, y, 'r-' )#, label='y=sin(x)' )
        del x,y
        self.ax.set_ylabel('y')
        self.ax.set_title('A beautiful sinewave function')
        self.ax.set_xlabel('x')
        self.ax.legend( loc='upper right', shadow=True )
        self.canvasPlot= self.fig.canvas
        self.nav = NavigationToolbar2Kivy( self.canvasPlot )

        # Adding plot and right panel
        self.ids.leftPanel.add_widget( self.nav.actionbar )
        self.ids.leftPanel.add_widget( self.canvasPlot )
        self.add_widget( self.rp )

        return

    def updatePlot( self, dataX, dataY ):
        self.ax.clear()
        self.ax.plot( dataX, dataY, 'r-' , label='Smartbench' )
        self.canvasPlot.draw()

    def plotTriggerPoint( self, x, y ):
        self.ax.plot( x, y, 'b*')
        self.canvasPlot.draw()
