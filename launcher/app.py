# -*- coding: utf-8 -*-

import os
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import platform
from glob import glob
from os.path import dirname, join, exists
import traceback

KIVYLAUNCHER_PATHS = os.environ.get("KIVYLAUNCHER_PATHS")

KV = """
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
        text: "K"
        size_hint_x: None
        width: self.height
    Label:
        text: "Kivy Launcher"
        size_hint_x: None
        width: self.texture_size[0]
        font_size: dp(16)
        font_name: "data/Roboto-Medium.ttf"


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
    RecycleView:
        id: rv
        viewclass: "LauncherEntry"
        RecycleBoxLayout:
            size_hint_y: None
            height: self.minimum_height
            orientation: "vertical"
            spacing: dp(2)
            default_size: None, dp(48)
            default_size_hint: 1, None
"""


class Launcher(App):
    def build(self):
        self.paths = [
            "/sdcard/kivy",
        ]
        if KIVYLAUNCHER_PATHS:
            self.paths.extend(KIVYLAUNCHER_PATHS.split(","))
        self.root = Builder.load_string(KV)
        self.refresh_entries()

    def refresh_entries(self):
        data = []
        for entry in self.find_entries(paths=self.paths):
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
        if paths is not None:
            for path in paths:
                for entry in self.find_entries(path=path):
                    yield entry
        elif path is not None:
            if not exists(path):
                return
            for filename in glob("{}/*/android.txt".format(path)):
                entry = self.read_entry(filename)
                if entry:
                    yield entry

    def read_entry(self, filename):
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
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        System = autoclass("java.lang.System")
        activity = PythonActivity.mActivity
        Intent = autoclass("android.content.Intent")
        String = autoclass("java.lang.String")

        j_entrypoint = String(entry.get("entrypoint"))
        j_orientation = String(entry.get("orientation"))

        intent = Intent(
            activity.getApplicationContext(),
            PythonActivity)
        intent.putExtra("entrypoint", j_entrypoint)
        intent.putExtra("orientation", j_orientation)
        activity.startActivity(intent)
        System.exit(0)
