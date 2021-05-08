"""This file contains a simple, editable app for the Kivy launcher.

Play, break an modify at will. :-)
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from textwrap import dedent
from os import popen


KV = dedent('''
<BarBase@GridLayout>:
    rows: 1
    padding: dp(4)
    size_hint_y: None
    height: dp(48)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: rgba("#3F51B5")
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    orientation: 'vertical'
    Label:
        canvas.before:
            Color:
                rgba: 0.2, 0.2, 0.6, 1
            Rectangle:
                pos: self.pos
                size: self.size
        size_hint_y: None
        height: "40dp"
        text: 'Script Runner'
        font_size: '20dp'
    BoxLayout:
        orientation: 'vertical'
        CodeInput:
            id: code_input
            text: "print('Hello world')  # Enter python code here and run."
        Splitter:
            sizable_from: 'top'
            TextInput:
                id: text_output
                text: "Click Run to see the output of the script"
    BarBase:
        Button:
            text: 'Run code'
            on_press: app.run_code(code_input.text)
        Button:
            text: 'Close'
            on_press: app.stop()
''')


class TestApp(App):
    def  build(self):
        self.main_box = Builder.load_string(KV)
        return self.main_box

    def run_code(self, text):
        """Run the code given in the CodeInput."""
        with open('code_main.py', 'w') as out_file:
            out_file.write(text)

        stream = popen('python code_main.py')
        self.main_box.ids.text_output.text = stream.read()

TestApp().run()