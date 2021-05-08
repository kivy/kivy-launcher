"""This file contains a simple server availability checker"""
from kivy.app import App
from kivy.lang.builder import Builder
from textwrap import dedent

SERVER_LIST = [('http://www.google.com', 80),
               ('https://www.google.com', 443),
               ('https://www.wikipedia.com', 443)]

KV = dedent('''
BoxLayout:
    orientation: 'vertical'
    Label:
        id: output_label
        text: 'Tap "Run" to start.'
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "40dp"
        Button:
            id: button_run
            text: 'Run'
        Button:
            text: 'Close'
            on_press: app.stop()
''')


class TestApp(App):
    """Core Kivy Application object."""

    def build(self):
        """Build and return our root widget."""
        return Builder.load_string(KV)


TestApp().run()
