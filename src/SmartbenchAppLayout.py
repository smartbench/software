""" Layout of Smartbench app and basic actions """

# Matplotlib includes
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

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

        self.plot = Plot(numberOfChannels=2)
        self.nav = NavigationToolbar2Kivy( self.plot.getCanvas() )

        # Adding plot and right panel
        self.ids.leftPanel.add_widget( self.nav.actionbar )
        self.ids.leftPanel.add_widget( self.plot.getCanvas() )
        self.add_widget( self.rp )

        return

    def setAxis(self, vec):
        self.plot.setAxis(vec)

    def updatePlot( self, dataX, dataY ):
        self.plot.updatePlot(dataX, dataY)

    def plotTriggerPoint( self, x, y ):
        self.plot.plotTriggerPoint(x,y)

    def getPlot(self):
        return self.plot


class Plot():

    def __init__(self, numberOfChannels):

        self.numberOfChannels = numberOfChannels
        self.fig, self.ax = plt.subplots()
        self.canvasPlot = self.fig.canvas
        self.channelColors = ['#ffffff', '#e6e600', '#e6e600', '#e6e600', '#e6e600', '#e6e600', '#e6e600', '#e6e600']

        self.ax.clear()
        """
        self.channelPlots = []
        for i in range(numberOfChannels):
            h, = self.ax.plot([],[], '-',color=self.channelColors[i], markersize=2, linewidth=3)
            self.channelPlots.append([h])
        """
        self.h1, = self.ax.plot([],[], '-',color='#ffffff', markersize=2, linewidth=3)

        self.ax.set_ylabel('Voltage [V]')
        self.ax.set_title('Smartbench')
        self.ax.set_xlabel('Time [sec]')
        self.ax.legend( loc='upper right', shadow=True )

        #self.ax.set_facecolor('grey')
        self.ax.set_facecolor('#1a1a1a')

        #self.ax.grid(color='r', linestyle='-', linewidth=2)
        self.ax.grid(linestyle='-', linewidth=2, color='#4d4d4d')

        self.setAxis([0, 150, 0, 256])

        return

    def getCanvas(self):
        return self.canvasPlot

    def clearPlot(self):
        self.ax.clear()

    def setAxis(self, vec):
        self.ax.axis(vec)
        self.ax.set_xticks(np.arange(vec[0], vec[1], (vec[1]-vec[0])/10))
        self.ax.set_yticks(np.arange(vec[2], vec[3], (vec[3]-vec[2])/10))
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        return

    def updatePlot( self, dataX, dataY ):
        self.h1.set_xdata(dataX)
        self.h1.set_ydata(dataY)
        self.canvasPlot.draw()
        return

    def plotTriggerPoint( self, x, y ):
        self.ax.plot( x, y, 'y*')
        self.canvasPlot.draw()
        return
