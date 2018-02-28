#!/usr/bin/python3

""" Main application for smartbench project """
'''
To run the server

    bokeh serve WebApp.py

Then navigate to the URL

    http://localhost:5006/WebApp

in your browser.

'''

#from pyftdi.ftdi import Ftdi
import serial
import time

import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.layouts import Spacer
from bokeh.models.widgets import Slider, TextInput
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure
from bokeh.palettes import Viridis3

from tornado import gen
import tornado

from OscopeApi import *
#from SmartbenchAppLayout import *
#from ScopeStatus import *
from Configuration_Definitions import *

# Useful line:
# yield tornado.gen.sleep(1)

# callbacks
# https://bokeh.pydata.org/en/latest/docs/reference/server/callbacks.html
# https://bokeh.pydata.org/en/latest/docs/reference/document.html#bokeh.document.document.Document

_STATUS_STOPPED = 0
_STATUS_RUNNING = 1

_CHANNEL_ON     = 1
_CHANNEL_OFF    = 0

DEBUG_ = True

class SmartbenchApp():
    #global source_chA, source_chB, doc, plot

    def __init__(self, doc, plot, source_chA, source_chB):

        self.doc = doc
        self.plot = plot
        self.source_chA = source_chA
        self.source_chB = source_chB
        self.status = _STATUS_STOPPED

        # Initializing oscope api
        self.smartbench = Smartbench()

        if(self.smartbench.isOpen()):

            # Default configuration
            self.configureScope()

            # Plot axes
            Nsamp = self.smartbench.get_number_of_samples()
            self.plot.x_range = Range1d(0, Nsamp-1)
            self.plot.y_range = Range1d(0,255)

            self.plot.xaxis[0].ticker=FixedTicker(ticks=np.arange(0,Nsamp-1,Nsamp/10))   #10 div
            self.plot.xgrid[0].ticker=FixedTicker(ticks=np.arange(0,Nsamp-1,Nsamp/10))
            #change yaxis ticker & ygrid ticker with fixed-width spacing
            self.plot.yaxis[0].ticker=FixedTicker(ticks=np.arange(0,255,256/10))   #10 div
            self.plot.ygrid[0].ticker=FixedTicker(ticks=np.arange(0,255,256/10))

            # Callback to start the acqusition, called as soon as possible
            # self.doc.add_next_tick_callback(self.newFrameCallback)
            #self.start()
        else:
            print("Device not connected!")
            #exit()

        return

    def start(self):
        self.status = _STATUS_RUNNING
        self.doc.add_next_tick_callback(self.newFrameCallback)
        return

    def stop(self):
        self.status = _STATUS_STOPPED

        try:    remove_timeout_callback(self.waitingTriggerCallback)
        except: pass
        try:    remove_timeout_callback(self.newFrameCallback)
        except: pass
        #try:    remove_next_tick_callback(self.newFrameCallback)
        #except: pass
        return

    def isRunning(self):
        return self.status == _STATUS_RUNNING

    def getSingleSeq(self):
        self.stop()
        self.smartbench.set_trigger_mode_single()
        self.start()
        return

    # --------------------------------------------------------
    # This method sends a "Start Request" to the device.
    # @gen.coroutine
    def newFrameCallback(self):
        if(self.status == _STATUS_STOPPED): return
        self.triggered      = 0
        self.buffer_full    = 0
        self.count          = 0
        printDebug("> Request Start")
        self.smartbench.request_start()
        #self.doc.add_next_tick_callback(self.waitingTriggerCallback) # Called as soon as possible
        self.doc.add_timeout_callback(self.waitingTriggerCallback, 500) # Called as soon as possible
        return

    # --------------------------------------------------------
    # This method will query the trigger status and the buffer status, which could
    # be {Triggered / Not triggered} and { buffer full / buffer not full } respectively.
    # Depending on the status, and the mode of operation (Normal or Auto) will wait or
    # not to show the data.
    # @gen.coroutine
    def waitingTriggerCallback(self):
        if(self.status == _STATUS_STOPPED): return
        printDebug("> Request Trigger Status")
        self.smartbench.request_trigger_status()
        printDebug("> Waiting...")
        self.buffer_full,self.triggered = self.smartbench.receive_trigger_status()
        printDebug("> Trigger={}\tBuffer_full={}".format( self.triggered, self.buffer_full ))

        if self.triggered==0 or self.buffer_full==0:
            if( self.smartbench.is_trigger_mode_single() or self.smartbench.is_trigger_mode_normal() ):
                self.doc.add_timeout_callback(self.waitingTriggerCallback,500) # Check again in 100 ms.
                return
            else:
                if(self.buffer_full == 1 and self.count < 5):
                    self.count = self.count + 1
                    self.doc.add_timeout_callback(self.waitingTriggerCallback,500) # Check again in 100 ms.
                    return

        # First, stops the capturing.
        printDebug("> Request Stop")
        self.smartbench.request_stop()

        # If channel is ON, requests the data.
        if(self.smartbench.chA.is_ch_on()):
            printDebug("> Request CHA")
            self.smartbench.request_chA()

            printDebug("> Waiting...")
            self.dataY_chA = list(reversed(self.smartbench.receive_channel_data()))
            self.dataX_chA = range(0,len(self.dataY_chA))
        else:
            self.dataY_chA = []
            self.dataX_chA = []

        # If channel is ON, requests the data.
        if(self.smartbench.chB.is_ch_on()):
            # Then, requests the data.
            printDebug("> Request CHB")
            self.smartbench.request_chB()

            printDebug("> Waiting...")
            self.dataY_chB = list(reversed(self.smartbench.receive_channel_data()))
            self.dataX_chB = range(0,len(self.dataY_chB))
        else:
            self.dataY_chB = []
            self.dataX_chB = []


        self.source_chA.data = dict(x=self.dataX_chA, y=self.dataY_chA)
        self.source_chB.data = dict(x=self.dataX_chB, y=self.dataY_chB)

        if( self.smartbench.is_trigger_mode_single()):
            self.stop()
        else:
            if(self.status == _STATUS_RUNNING):
                self.doc.add_next_tick_callback(self.newFrameCallback ) # Called as soon as possible

        return


    def configureScope(self):
        self.smartbench.setDefaultConfiguration()

        # # For a good visualization with "Fake_ADC", clk divisor must be 1.
        # # ADC CLOCK SET TO 20MHz
        # self.smartbench.chA.set_clk_divisor(Configuration_Definitions.Clock_Adc_Div_Sel[13])
        # self.smartbench.chB.set_clk_divisor(Configuration_Definitions.Clock_Adc_Div_Sel[13]) # not necessary, ignored
        # # AVERAGE DISABLED (1 SAMPLE)
        self.smartbench.chA.set_nprom(Configuration_Definitions.Mov_Ave_Sel[13])
        self.smartbench.chB.set_nprom(Configuration_Definitions.Mov_Ave_Sel[13])

        return


if __name__ == '__main__':
    try:
        sm = SmartbenchApp()
        #sm.run()
    except KeyboardInterrupt:
        print ("Interrupted")
        sm.smartbench.oscope.close()
        exit()
