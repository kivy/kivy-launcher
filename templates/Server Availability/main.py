"""This file contains a simple server availability checker"""
from kivy.app import App
from kivy.lang.builder import Builder
from textwrap import dedent
from kivy.clock import Clock
import socket

SERVER_LIST = [('www.google.com', 80),
               ('www.google.com', 443),
               ('www.wikipedia.com', 443),
               ('fail.me.now!', 0)]

KV = dedent('''
BoxLayout:
    orientation: 'vertical'
    Label:
        canvas.before:
            Color:
                rgba: 0.2, 0.2, 0.2, 1
            Rectangle:
                pos: self.pos
                size: self.size
        id: output_label
        text: 'Tap "Run" to start.'
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "40dp"
        Button:
            id: button_run
            text: 'Run'
            on_press: app.start_check()
        Button:
            text: 'Close'
            on_press: app.stop()
''')


class TestApp(App):
    """Core Kivy Application object."""

    _running = False
    """Tracks whether on not we are still running our checks."""

    def build(self):
        """Build and return our root widget."""
        return Builder.load_string(KV)

    def start_check(self):
        """Start our availability check."""
        if self._running:
            return

        self.root.ids.disabled = True
        self.add_text()
        self._run_checks([i for i in SERVER_LIST])

    def _run_checks(self, site_list):
        """Run the check for our next website."""
        item = site_list.pop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if sock.connect_ex(item) == 0:
                self.add_text(f'Site available: {item}')
            else:
                self.add_text(f'Site down! {item}')
        except Exception as e:
            self.add_text(f'Error connecting to {item}')
            self.add_text(f'Error was {e}')

        if site_list:
            Clock.schedule_once(lambda dt: self._run_checks(site_list))

    def add_text(self, text=None):
        """Add the require text line to the label. Clear if None."""
        label = self.root.ids.output_label
        label.text = label.text + '\n' + text if text else 'Starting check...'


TestApp().run()
