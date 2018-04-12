"""
Switch Container
================

.. author:: Mathieu Virbel <mat@meltingrocks.com>

A simpler version of ScreenManager.
"""

from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty


class SwitchContainer(RelativeLayout):

    index = NumericProperty(0)

    def __init__(self, **kwargs):
        self.widgets = []
        super(SwitchContainer, self).__init__(**kwargs)
        self.refresh_from_index()

    def add_widget(self, widget):
        self.widgets.append(widget)
        self.refresh_from_index()

    def remove_widget(self, widget):
        self.widgets.remove(widget)
        self.refresh_from_index()

    def on_index(self, instance, value):
        self.refresh_from_index()

    def refresh_from_index(self):
        index = self.index
        for widget in self.widgets:
            super(SwitchContainer, self).remove_widget(widget)
        if index > len(self.widgets):
            index = 0
        if not len(self.widgets):
            return
        super(SwitchContainer, self).add_widget(self.widgets[index])
