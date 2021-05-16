"""This file contains a simple, editable app for the Kivy launcher.

Play, break an modify at will. :-)
"""
from kivy.app import App
from kivy.lang.builder import Builder
from textwrap import dedent

KV = dedent('''
BoxLayout:
    Button:
        text: "Close me"
        on_press: app.stop()
    Button:
        text: "Change me"
        on_press: self.text = "Press" if self.text == "Click" else "Click"
''')


class TestApp(App):
    """Minimal Kivy App for demo purposes."""

    def build(self):
        """Build and return the root widget."""
        return Builder.load_string(KV)


TestApp().run()
