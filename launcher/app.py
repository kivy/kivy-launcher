# -*- coding: utf-8 -*-

import os
from datetime import datetime
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import platform
from kivy.properties import ListProperty, BooleanProperty
from glob import glob
from os.path import dirname, join, exists
import traceback

KIVYLAUNCHER_PATHS = os.environ.get("KIVYLAUNCHER_PATHS")

KV = r"""
#:import A kivy.animation.Animation
#:import rgba kivy.utils.get_color_from_hex
#:set ICON_PLAY "P"
#:set ICON_REFRESH "R"
#:set ICON_KIVY "K"

<IconLabel@Label>:
    font_name: "data/kivylauncher.ttf"

<IconButton@ButtonBehavior+IconLabel>
    size_hint_x: None
    width: self.height
    canvas.before:
        Color:
            rgba: rgba("#ffffff66") if self.state == "down" else rgba("#00000000")
        Rectangle:
            pos: self.pos
            size: self.size

<LLabel@Label>:
    text_size: self.width, None

<TopBar@GridLayout>:
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

    IconLabel:
        text: ICON_KIVY
        size_hint_x: None
        width: self.height
    Label:
        text: "Kivy Launcher"
        size_hint_x: None
        width: self.texture_size[0]
        font_size: dp(16)
        font_name: "data/Roboto-Medium.ttf"

    IconButton:
        text: ICON_REFRESH
        on_press:
            app.refresh_entries()

    ToggleButton:
        text: 'Logs'
        state: 'down' if app.display_logs else 'normal'
        on_state:
            app.display_logs = self.state == 'down'


<LauncherEntry@BoxLayout>:
    data_title: ""
    data_orientation: ""
    data_logo: "data/logo/kivy-icon-64.png"
    data_orientation: ""
    data_author: ""
    data_entry: None
    padding: dp(4)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: rgba("#eeeef0")
        Rectangle:
            pos: self.x + self.height + self.padding[0], self.y - self.padding[1] / 2.
            size: self.width, dp(1)

    Image:
        source: root.data_logo
        size_hint_x: None
        width: self.height
    BoxLayout:
        orientation: "vertical"
        padding: 0, dp(4)
        LLabel:
            text: root.data_title
            color: rgba("#454547")
            font_name: "data/Roboto-Medium.ttf"
            font_size: dp(13)
        LLabel:
            text: root.data_author
            color: rgba("#b4b6b7")
            font_size: dp(11)
    IconButton:
        text: ICON_PLAY
        on_release: app.start_activity(root.data_entry)
        color: rgba("#b4b6b8")


GridLayout:
    cols: 1
    canvas.before:
        Color:
            rgba: rgba("#fafafc")
        Rectangle:
            size: self.size
    TopBar
    FloatLayout:
        RecycleView:
            id: rv
            pos_hint: {'pos': (0, 0)}
            viewclass: "LauncherEntry"
            RecycleBoxLayout:
                size_hint_y: None
                height: self.minimum_height
                orientation: "vertical"
                spacing: dp(2)
                default_size: None, dp(48)
                default_size_hint: 1, None

        RecycleView:
            viewclass: 'LogLabel'
            data: [{'text': log} for log in app.logs]
            _top: 0
            pos_hint: {'top': self._top, 'x': 0}
            visible: app.display_logs
            on_visible:
                A.cancel_all(self, '_top')
                A(_top=1 if self.visible else 0, d=.3, t='out_quad').start(self)

            canvas.before:
                Color:
                    rgba: rgba("#CCCCCCCC")
                Rectangle:
                    pos: self.pos
                    size: self.size

            RecycleBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                default_size_hint: None, None
                default_size: 0, 20
                padding: 5, 5

        Label:
            text:
                '''
                Please install applications in one of the following directories
                - {}
                '''.format('\n -'.join(app.paths))
            pos_hint: {'pos': (0, 0)}
            color: rgba("#222222" if not rv.data else "#00000000")

<LogLabel@Label>:
    color: rgba("#222222FF")
    pos_hint: {'x': 0}
    width: self.texture_size[0]
"""


class Launcher(App):
    paths = ListProperty()
    logs = ListProperty()
    display_logs = BooleanProperty(False)

    def log(self, log):
        print(log)
        self.logs.append(f"{datetime.now().strftime('%X.%f')}: {log}")

    def build(self):
        self.log('start of log')
        if KIVYLAUNCHER_PATHS:
            self.paths.extend(KIVYLAUNCHER_PATHS.split(","))
        else:
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            sdcard_path = Environment.getExternalStorageDirectory().getAbsolutePath()
            self.paths = [
                sdcard_path + "/kivy",
            ]

        self.root = Builder.load_string(KV)
        self.refresh_entries()

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE])

    def refresh_entries(self):
        data = []
        self.log('starting refresh')
        for entry in self.find_entries(paths=self.paths):
            self.log(f'found entry {entry}')
            data.append({
                "data_title": entry.get("title", "- no title -"),
                "data_path": entry.get("path"),
                "data_logo": entry.get("logo", "data/logo/kivy-icon-64.png"),
                "data_orientation": entry.get("orientation", ""),
                "data_author": entry.get("author", ""),
                "data_entry": entry
            })
        self.root.ids.rv.data = data

    def find_entries(self, path=None, paths=None):
        self.log(f'looking for entries in {paths} or {path}')
        if paths is not None:
            for path in paths:
                for entry in self.find_entries(path=path):
                    yield entry

        elif path is not None:
            if not exists(path):
                self.log(f'{path} does not exist')
                return

            self.log('{os.listdir(path)}')
            for filename in glob("{}/*/android.txt".format(path)):
                self.log(f'{filename} exist')
                entry = self.read_entry(filename)
                if entry:
                    yield entry

    def read_entry(self, filename):
        self.log(f'reading entry {filename}')
        data = {}
        try:
            with open(filename, "r") as fd:
                lines = fd.readlines()
                for line in lines:
                    k, v = line.strip().split("=", 1)
                    data[k] = v
        except Exception as e:
            traceback.print_exc()
            return None
        data["entrypoint"] = join(dirname(filename), "main.py")
        data["path"] = dirname(filename)
        icon = join(data["path"], "icon.png")
        if exists(icon):
            data["icon"] = icon
        return data

    def start_activity(self, entry):
        if platform == "android":
            self.start_android_activity(entry)
        else:
            self.start_desktop_activity(entry)

    def start_desktop_activity(self, entry):
        import sys
        from subprocess import Popen
        entrypoint = entry["entrypoint"]
        env = os.environ.copy()
        env["KIVYLAUNCHER_ENTRYPOINT"] = entrypoint
        main_py = os.path.realpath(os.path.join(
            os.path.dirname(__file__), "..", "main.py"))
        cmd = Popen([sys.executable, main_py], env=env)
        cmd.communicate()

    def start_android_activity(self, entry):
        self.log('starting activity')
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        System = autoclass("java.lang.System")
        activity = PythonActivity.mActivity
        Intent = autoclass("android.content.Intent")
        String = autoclass("java.lang.String")

        j_entrypoint = String(entry.get("entrypoint"))
        j_orientation = String(entry.get("orientation"))

        self.log('creating intent')
        intent = Intent(
            activity.getApplicationContext(),
            PythonActivity
        )
        intent.putExtra("entrypoint", j_entrypoint)
        intent.putExtra("orientation", j_orientation)
        self.log(f'ready to start intent {j_entrypoint} {j_orientation}')
        activity.startActivity(intent)
        self.log(f'activity started')
        System.exit(0)
