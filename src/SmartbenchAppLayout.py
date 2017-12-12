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
from kivy.uix.switch import Switch

from kivy.garden.knob import Knob

from Plot import *

#baseText = ("Run it again?","Press me to \nstop the \nsinewave")
statusBtnText = ["Start", "Stop"]
_STATUS_STOPPED = 0
_STATUS_RUNNING = 1

class rightPanel(BoxLayout):
    status = _STATUS_RUNNING
    btText = StringProperty(statusBtnText[status])
    k = 0
    #self.statusChangeSignal

    def __init__( self, **kwargs):
        super( rightPanel, self).__init__()
        #self.ids.kn._value(self.ids.kn,self.ids.kn.value)
        self.ids.cha_vdiv._value(self.ids.cha_vdiv,self.ids.cha_vdiv.value)
        #self.switch = Switch(active=True)
        #self.switch.bind(active=callbackSwitchOn)
        #self.ids.btn_ChA_On.group = 'grp_cha_on_off'
        #self.ids.btn_ChA_Off.group = 'grp_cha_on_off'


    # Button pressed. Call method 'statusChangeSignal'
    def btnStatusPressed(self):
        try:    self.statusChangeSignal(self.status)
        except: pass
        return

    # Set the method that will be called when the button is pressed
    def setStatusChangeSignal(self, signal):
        self.statusChangeSignal = signal
        return

    # Updates the current status, and the button's text.
    def statusChanged(self, status):
        self.status = status
        self.btText = statusBtnText[status]
        return

class MainWindow(BoxLayout, Plot):

    def __init__(self,**kwargs):
        #If a user attempts to run your application with a version of Kivy that is older than the specified version, an Exception is raised
        kivy.require('1.0.1')

        self.rp = rightPanel()
        super(MainWindow, self).__init__()

        self.nav = NavigationToolbar2Kivy( self.getCanvas() )

        # Adding plot and right panel
        self.ids.leftPanel.add_widget( self.nav.actionbar )
        self.ids.leftPanel.add_widget( self.getCanvas() )
        self.add_widget( self.rp )

        return

    # Set the method that will be called when the button is pressed
    def setStatusChangeSignal(self, signal):
        self.rp.setStatusChangeSignal(signal)
        return

    # Status changed --> tell RightPanel so it will update it's status.
    def statusChanged(self, status):
        self.rp.statusChanged(status)
        return
