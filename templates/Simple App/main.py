"""This file contains a simple, editable app for the Kivy launcher.

Play, break an modiy at will. :-)
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from textwrap import dedent

KV = dedent('''
<MainBox>:
    Button:
        text: "Close me"
        on_press: root.app.stop()
    Button:
        text: "Change me"
        on_press: self.text = "Press" if self.text == "Click" else "Click"
''')

class  MainBox(BoxLayout):
    def __init__(self, app):
        super().__init__()
        self.app = app


class TestApp(App):
    def  build(self):
        Builder.load_string(KV)
        return MainBox(app=self)


TestApp().run()