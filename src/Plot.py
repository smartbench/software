
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



class Plot():

    def __init__(self):

        self.fig, self.ax = plt.subplots()
        self.canvasPlot = self.fig.canvas
        #self.channelColors = ['#ffffff', '#e6e600', '#e6e600', '#e6e600', '#e6e600', '#e6e600', '#e6e600', '#e6e600']

        self.ax.clear()

        self.channelPlots = []

        self.ax.set_ylabel('Voltage [V]')
        self.ax.set_title('Smartbench')
        self.ax.set_xlabel('Time [sec]')
        self.ax.legend( loc='upper right', shadow=True )

        #self.ax.set_facecolor('grey')
        self.ax.set_facecolor('#1a1a1a')

        #self.ax.grid(color='r', linestyle='-', linewidth=2)
        self.setGrid(linestyle='-', linewidth=2, color='#4d4d4d')
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

    def channelClear( self, channel):
        channel.set_xdata([])
        channel.set_ydata([])
        self.canvasPlot.draw()
        return

    def channelRefresh( self, dataX, dataY, channel ):
        channel.set_xdata(dataX)
        channel.set_ydata(dataY)
        self.canvasPlot.draw()
        return

    def addChannel( self, *args, **kwargs):
        if 'color' in kwargs:
            h, = self.ax.plot([],[], *args, **kwargs)
        else:
            h, = self.ax.plot([],[], color='#ffffff', *args, **kwargs)
        #h, = self.ax.plot([],[], *args, **kwargs)
        self.channelPlots.append([h])
        return h

    def setGrid(self, *args, **kwargs):
        self.ax.grid(*args, **kwargs)
        return
