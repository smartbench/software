from kivy.app import App
import itertools
from math import sin
from gardengraph_ import Graph, MeshLinePlot
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as rgb
from kivy.uix.boxlayout import BoxLayout

class TestApp(App):
    def build(self):
        b = BoxLayout(orientation='vertical')
        graph = Graph(xlabel='X', ylabel='Y', x_ticks_minor=5,
            x_ticks_major=25, y_ticks_major=1,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=-1, ymax=1)
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        graph.add_plot(plot)
        self.plot = plot

        # Comentar siguiente línea para graico fijo
        Clock.schedule_interval(self.update_points, 1 / 60.)

        b.add_widget(graph)
        return b

    def update_points(self, *args):
        self.plot.points = [(x / 10., sin(Clock.get_time() + x / 50.)) for x in range(-500, 501)]

TestApp().run()
