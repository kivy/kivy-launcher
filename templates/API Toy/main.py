"""This file contains a simple API Tool for making POST/GET req quests."""
from json import dumps
from kivy.app import App
from kivy.lang.builder import Builder
from textwrap import dedent
from kivy.clock import Clock
import requests


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
                text: 'http://127.0.0.1:9001/zenplayer/get_state'
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
            id: lbl_response
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
        Clock.schedule_once(lambda dt: self._make_request_clock(req_type))

    def _make_request_clock(self, req_type):
        """Make the given call."""
        meth = getattr(requests, req_type)
        response = meth(self.main_box.ids.ti_url.text)

        text = f'Status code: {response.status_code}\n\n'
        if response.headers.get('content-type') == 'application/json':
            text += f'{dumps(response.json(), indent=4)}'
        else:
            text += f'Content: {response.content.decode("UTF-8")}'
        self.main_box.ids.lbl_response.text = text


if __name__ == '__main__':
    APIToyApp().run()
