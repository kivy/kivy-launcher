"""This file contains a simple API Tool for making POST/GET req quests."""
from kivy.app import App
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
        text: 'API Toy'
        font_size: '20dp'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            height: "40dp"
            size_hint_y: None
            Label:
                text: 'URL :'
                size_hint: [0.3, 1]
            TextInput:
                id: ti_url
                text: 'http://127.0.0.1:9001'
                size_hint: [0.7, 1]
        BoxLayout:
            height: "40dp"
            size_hint_y: None
            Label:
                text: 'Token :'
                size_hint: [0.3, 1]
            TextInput:
                id: ti_token
                size_hint: [0.7, 1]
        Label:
            text: 'Tap GET or POST to retrieve a response.'

    BarBase:
        Button:
            text: 'GET'
            on_press: app.make_request('get')
        Button:
            text: 'POST'
            on_press: app.make_request('post')
        Button:
            text: 'Close'
            on_press: app.stop()
''')


class APIToyApp(App):
    """Simple Kivy app showing how to make and response to API calls."""

    def build(self):
        """Build and return the root widget."""
        self.main_box = Builder.load_string(KV)
        return self.main_box

    def make_request(self, req_type):
        """Perform the specified type of HTTP request."""
        pass


if __name__ == '__main__':
    APIToyApp().run()
