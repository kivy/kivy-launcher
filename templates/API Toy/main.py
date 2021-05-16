"""This file contains a simple API Tool for making POST/GET req quests."""
from json import dumps, loads
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
                text: 'http://postman-echo.com/get'
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
                hint_text: 'The Bearer Token so use. Leave blank for None.'
        BoxLayout:
            height: "40dp"
            size_hint_y: None
            Label:
                text: 'Payload :'
                size_hint: [0.3, 1]
            TextInput:
                id: ti_payload
                size_hint: [0.7, 1]
                hint_text: 'The data payload so use. Leave blank for None.'
        Label:
            id: lbl_response
            text: 'Tap GET, POST, PUT or DELETE to retrieve a response.'
            text_size: root.width * 0.9, None
            halign: 'center'
            size: self.texture_size
    BarBase:
        Button:
            text: 'GET'
            on_press: app.make_request('get')
        Button:
            text: 'POST'
            on_press: app.make_request('post')
        Button:
            text: 'PUT'
            on_press: app.make_request('put')
        Button:
            text: 'DELETE'
            on_press: app.make_request('delete')
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

    def _get_headers(self):
        """Return a dictionary of the request headers, else None."""
        token = self.main_box.ids.ti_token.text
        return {"Authorization": f"Bearer {token}"} if token else None

    def _get_data(self):
        """Return a dictionary of the request data, else None."""
        data = self.main_box.ids.ti_payload.text
        return None if not data else loads(data)

    def _display_response(self, response):
        """Dislay the details of the response object."""
        text = f'Status code: {response.status_code}\nResponse type: ' \
            f'{response.headers.get("content-type")}\n\n'
        if response.headers.get('content-type') == 'application/json':
            text += f'{dumps(response.json(), indent=4)}'
        else:
            text += f'Content: {response.content.decode("UTF-8")}'

        self.main_box.ids.lbl_response.text = text
        self.main_box.ids.lbl_response.color = [0.5, 1.0, 0.5, 1.0] \
            if response.status_code == 200 else [1.0, 0.5, 0.5, 1.0]

    def _make_request_clock(self, req_type):
        """Make the given call."""
        meth = getattr(requests, req_type)
        headers = self._get_headers()
        data = self._get_data()
        try:
            response = meth(
                self.main_box.ids.ti_url.text, headers=headers, data=data)
            self._display_response(response)
        except Exception as e:
            self.main_box.ids.lbl_response.text = f"Error calling API: {e}"
            self.main_box.ids.lbl_response.color = [1.0, 0.5, 0.5, 1.0]


if __name__ == '__main__':
    APIToyApp().run()
