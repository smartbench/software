#!/usr/bin/python3

""" Main application for smartbench project """

from kivy.app import App

#from pyftdi.ftdi import Ftdi
import serial
import time
#from math import sin,pi

from OscopeApi import *
from SmartbenchAppLayout import *

class SmartbenchApp(App):
    title = 'SmartbenchApp'
    def build(self):

        # Kivy App initialization
        super(SmartbenchApp, self).__init__()

        self.count = 0

        # Initializing oscope api
        self.smartbench = Smartbench()

        # Default configuration
        self.setDefaultConfiguration()

        # Window initialization
        self.mw = MainWindow()

        # continue here!
        # testing kivy updating upon failure on opening port
        # toDo: Add an option so the users can let the App that they connected a device
        if self.smartbench.get_oscope_status() == False:
            self.mw.orientation = 'vertical'

        # This starts the application flow
        Clock.schedule_once(self.newFrameCallback) # Called as soon as possible

        return self.mw

    # --------------------------------------------------------
    # This method sends a "Start Request" to the device.
    def newFrameCallback(self,dt):
        self.triggered      = 0
        self.buffer_full    = 0
        self.count          = 0
        print("> Request Start")
        self.smartbench.request_start()
        Clock.schedule_once(self.waitingTriggerCallback) # Called as soon as possible
        return

    # --------------------------------------------------------
    # This method will query the trigger status and the buffer status, which could
    # be {Triggered / Not triggered} and { buffer full / buffer not full } respectively.
    # Depending on the status, and the mode of operation (Normal or Auto) will wait or
    # not to show the data.
    def waitingTriggerCallback(self,dt):
        print("> Request Trigger Status")
        self.smartbench.request_trigger_status()
        print("> Waiting...")
        self.buffer_full,self.triggered = self.smartbench.receive_trigger_status()
        print("> Trigger={}\tBuffer_full={}".format( self.triggered, self.buffer_full ))

        if self.triggered==0 or self.buffer_full==0:
            if( self.smartbench.is_trigger_mode_single() or self.smartbench.is_trigger_mode_normal() ):
                Clock.schedule_once(self.waitingTriggerCallback,0.5) # Check again in 500 ms.
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


        self.mw.updatePlot( self.dataX, self.dataY )
        self.mw.plotTriggerPoint( self.smartbench.get_pretrigger()-1, self.smartbench.get_trigger_value() )

        if( self.smartbench.is_trigger_mode_auto() or self.smartbench.is_trigger_mode_normal() ):
            Clock.schedule_once( self.newFrameCallback ) # Called as soon as possible

        return


    def setDefaultConfiguration(self):
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

        self.smartbench.set_trigger_mode_normal()

        return


if __name__ == '__main__':
    try:
        sm = SmartbenchApp()
        sm.run()
    except KeyboardInterrupt:
        print ("Interrupted")
        sm.smartbench.oscope.close()
        exit()
