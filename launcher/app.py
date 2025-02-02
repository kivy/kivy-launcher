# -*- coding: utf-8 -*-

import os
from datetime import datetime
from kivy.utils import platform
if platform == "android":
    from jnius import autoclass, cast
from kivy.lang import Builder
from kivy.app import App
from kivy.properties import ListProperty, BooleanProperty, StringProperty
from os.path import dirname, join, exists
import traceback


KIVYLAUNCHER_PATHS = os.environ.get("KIVYLAUNCHER_PATHS")

class Launcher(App):
    paths = ListProperty()
    logs = StringProperty()
    display_logs = BooleanProperty(False)

    def on_request_close(self, *args):
        import sys
        sys.exit(0)

    def log(self, log):
        self.logs += f"{datetime.now().strftime('%X.%f')}: {log}\n\n"

    # try to do this, it will allow you to have access to all directories and files in the storage.
    def permissions_external_storage(self, *args):
        from android import api_version  # 30
        self.log(f'sdk: {api_version}')

        if api_version > 29:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Environment = autoclass("android.os.Environment")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            # If you have access to the external storage, do whatever you need
            if Environment.isExternalStorageManager():
                # If you don't have access, launch a new activity to show the user the system's dialog
                # to allow access to the external storage
                pass
            else:
                try:
                    activity = PythonActivity.mActivity.getApplicationContext()
                    uri = Uri.parse("package:" + activity.getPackageName())
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                    currentActivity = cast(
                        "android.app.Activity", PythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)
                except:
                    intent = Intent()
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    currentActivity = cast(
                        "android.app.Activity", PythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)

    def build(self):
        self.log('start of log')

        if platform != 'android':
            from kivy.core.window import Window
            Window.bind(on_request_close=self.on_request_close)

        if KIVYLAUNCHER_PATHS:
            self.paths.extend(KIVYLAUNCHER_PATHS.split(","))

        if platform == 'android':
            Environment = autoclass('android.os.Environment')
            sdcard_path = Environment.getExternalStorageDirectory()\
                .getAbsolutePath()
            self.paths = [sdcard_path + "/kivy",
                          sdcard_path + '/Download/kivy']
            try:
                from android.storage import app_storage_path
                self.paths.append(join(app_storage_path(), 'app', 'kivy'))
            except Exception as e:
                self.log(f'{e}')
        else:
            self.paths = [os.path.expanduser("./kivy")]

        self.root = Builder.load_file("launcher/app.kv")

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE])
            try:
                self.permissions_external_storage()
            except Exception:
                self.log(traceback.format_exc())

        self.refresh_entries()

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
        if data:
            tl = self.root.ids.tl
            if tl.parent:
                tl.parent.remove_widget(tl)


    def find_entries(self, path=None, paths=None):
        self.log(f'looking for entries in {paths} or {path}')
        try:
            if paths is not None:
                for path in paths:
                    for entry in self.find_entries(path=path):
                        yield entry

            elif path is not None:
                if not exists(path):
                    self.log(f'{path} does not exist')
                    return

                self.log(f'{os.listdir(path)}')
                for filename in os.listdir(path):
                    filename = join(path, filename, 'android.txt')
                    if exists(filename):
                        self.log(f'{filename} exist')
                    else:
                        self.log(f'{filename} not exist')
                        continue
                    entry = self.read_entry(filename)
                    if entry:
                        yield entry
        except Exception as e:
            self.log(f'{e}')
            return []

    def read_entry(self, filename):
        self.log(f'reading entry {filename}')
        data = {}
        try:
            with open(filename, "r", encoding='utf-8') as fd:
                lines = fd.readlines()
                for line in lines:
                    k, v = line.strip().split("=", 1)
                    data[k] = v
        except Exception:
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
        # sys.exit(0)

    def start_android_activity(self, entry):
        self.log('starting activity')
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
        self.log('activity started')
        System.exit(0)
