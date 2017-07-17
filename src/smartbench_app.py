""" Smartbench app

This app is the computer-side part of Smartbench project.
You can control the scope, see the measured signal and posprocess it.

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

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                NavigationToolbar2Kivy


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from math import sin,pi


x = range(0,500)
y = [ sin(2*pi*i/500.) for i in range(0,500) ]

fig, ax = plt.subplots()
rects = ax.plot( x, y, 'r-' , label='y=sin(x)' )
ax.set_ylabel('y')
ax.set_title('A beautiful sinewave function')
ax.set_xlabel('x')
ax.legend( loc='upper right', shadow=True )

canvas = fig.canvas

class SmartbenchApp(App):
    title = 'SmartbenchApp'

    def build(self):
        fl = BoxLayout(orientation="vertical")
        nav = NavigationToolbar2Kivy(canvas)
        fl.add_widget(nav.actionbar)
        fl.add_widget(canvas)
        return fl

if __name__ == '__main__':
    SmartbenchApp().run()
