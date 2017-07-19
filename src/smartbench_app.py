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
rects = ax.plot( x, y, 'r-' , label='y=sin(x)' )
ax.set_ylabel('y')
ax.set_title('A beautiful sinewave function')
ax.set_xlabel('x')
ax.legend( loc='upper right', shadow=True )

canvas= fig.canvas
nav = NavigationToolbar2Kivy(canvas)
#nav_act = nav.actionbar

# root = Builder.load_string( '''
# BoxLayout:
#     orientation: 'horizontal'                                               # 'vertical'
#     spacing: 10                                                             # in pixels
#     ActionBar:
#         id: nav_act
#     FigureCanvasKivy:     ## ACA la caga
#         id: canvas
#     BoxLayout:
#         orientation: 'vertical'
#         spacing: 10
#         Knob:
#             #size_hint: (.9,1)
#             value: 0
#             knobimg_source: "img/knob_black.png"
#             markeroff_color: 0.0, 0.0, .0, 1
#             knobimg_size: 0.9
#             marker_img: "img/bline3.png"
#         Label:
#             text: "Hola mundo"
#         Button:
#         ''')


class SmartbenchApp(App):
    title = 'SmartbenchApp'
    def build(self):
        #return root        # Me CANSE DEL KIVI LANGUAGE JAJA
        fl = BoxLayout(orientation="horizontal",spacing=10)
        fl2 = BoxLayout(orientation="vertical",spacing=10)
        fl2.add_widget(nav.actionbar)
        fl2.add_widget(canvas)
        fl3 = BoxLayout(orientation="vertical",spacing=10)
        knob=Knob(
        #size_hint=(0.7,1),
        value=0,
        knobimg_source = "img/knob_black.png",
        markeroff_color = (0.0, 0.0, .0, 1),
        knobimg_size = 0.9,
        marker_img = "img/bline3.png",
        )
        label=Label(text= "Hola mundo")
        button=Button(text= "Press me, bitch")
        fl3.add_widget(knob)
        fl3.add_widget(label)
        fl3.add_widget(button)
        fl.add_widget(fl2)
        fl.add_widget(fl3)
        return fl

if __name__ == '__main__':
    SmartbenchApp().run()
