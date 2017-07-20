""" Smartbench app

This app is the computer-side part of Smartbench project.
You can control the scope, see the measured signal and do some post-processing.

Authors:
            IP      Ivan Santiago Paunovic

Version:
            Date            Number          Name            Modified by     Comment
            2017/07/17      0.1             SmBegins_mplf   IP              First approach. Using garden.matplotlib.

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

from kivy.uix.actionbar import ActionBar
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

from kivy.garden.knob import Knob

from math import sin,pi


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

root = Builder.load_string( '''
BoxLayout:
    orientation: 'horizontal'                                               # 'vertical'
    spacing: 10                                                             # in pixels
    BoxLayout:
        id: leftPanel
        orientation: 'vertical'
        spacing: 10
''')
root.ids.leftPanel.add_widget(nav.actionbar)
root.ids.leftPanel.add_widget(canvas)

rightPanel = Builder.load_string( '''
BoxLayout:
    orientation: 'vertical'
    spacing: 10
    Knob:
        #size_hint: (.9,1)
        value: 0
        knobimg_source: "img/knob_black.png"
        markeroff_color: 0.0, 0.0, .0, 1
        knobimg_size: 0.9
        marker_img: "img/bline3.png"
    Label:
        text: "Hola mundo"
    Button:
        text: "Press me, bitch"
''')

root.add_widget(rightPanel)

class SmartbenchApp(App):
    title = 'SmartbenchApp'
    def build(self):
        return root

def myCallback(dt):
    myCallback.k = myCallback.k + 10
    y = [ sin(2*pi*(i-myCallback.k)/500.) for i in range(0,500) ]
    ax.clear()
    ax.plot( x, y, 'r-' , label='y=sin(x)' )
    canvas.draw()
    #print 'tick ...'
myCallback.k=0 #initial value of static local variable k

Clock.schedule_interval(myCallback,0.1)


if __name__ == '__main__':
    SmartbenchApp().run()
