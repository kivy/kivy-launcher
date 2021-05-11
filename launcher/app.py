# -*- coding: utf-8 -*-

import os
from datetime import datetime
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import platform
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty
from glob import glob
from os.path import dirname, join, exists
import traceback
from shutil import copytree


KIVYLAUNCHER_PATHS = os.environ.get("KIVYLAUNCHER_PATHS")


class Launcher(App):
    paths = ListProperty()
    logs = ListProperty()
    display_logs = BooleanProperty(False)
    current_entry = ObjectProperty()

    def log(self, log):
        print(log)
        self.logs.append(f"{datetime.now().strftime('%X.%f')}: {log}")

    def build(self):
        self.log('start of log')

        try:
            self.paths = [f'{self._get_user_data_dir()}/apps']
            if KIVYLAUNCHER_PATHS:
                self.paths.extend(KIVYLAUNCHER_PATHS.split(","))

            self.create_templates(self.paths[0])
        except Exception as e:
            self.paths = []
            self.log(f"Error {e}")

        self.root = Builder.load_file("launcher/app.kv")
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

            self.log(f'listing: {os.listdir(path)}')
            for filename in glob("{}/*/android.txt".format(path)):
                self.log(f'{filename} entry exists')
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
            AndroidActivity.start_android_activity(self.log, entry)
        else:
            self.start_desktop_activity(entry)

    def edit_activity(self, entry):
        """Open the selected activity in our  code launcher."""
        with open(entry['entrypoint'], "r") as f:
            self.root.ids.code_editor.text = f.read()

        self.current_entry = entry
        self.root.current = "editor"

    def edit_activity_save(self):
        """Save the editing activity."""
        with open(self.current_entry['entrypoint'], "w") as f:
            f.write(self.root.ids.code_editor.text)

        self.root.current = "launcher"

    def edit_activity_close(self):
        """Close the editing activity."""
        self.root.current = "launcher"

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


    def create_templates(self, kivy_path):
        """Create the initial templates if a kivy folder does not  exist."""
        self.log(f'create_template: path {kivy_path}')
        self.log(f'exists={exists(kivy_path)}')
        if not exists(kivy_path):
            try:
                os.makedirs(kivy_path)
                copytree('./templates', kivy_path, dirs_exist_ok=True)
            except Exception as e:
                self.log(f"Unable to create templates: {e}")


class AndroidActivity:
    """This class manages the ceation and closing of activities."""

    _activity = None

    @staticmethod
    def start_android_activity(log, entry):
        """Start a new PythonActivity based on the given entry.

        Args:
            log (callable): The log function accepting a message parameter.
            entry (dict): A dict representing the loaded entry

        """
        log('starting activity')
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        System = autoclass("java.lang.System")
        AndroidActivity._activity = activity = PythonActivity.mActivity
        Intent = autoclass("android.content.Intent")
        String = autoclass("java.lang.String")

        j_entrypoint = String(entry.get("entrypoint"))
        j_orientation = String(entry.get("orientation"))

        log('creating intent')
        intent = Intent(
            activity.getApplicationContext(),
            PythonActivity
        )
        intent.putExtra("entrypoint", j_entrypoint)
        intent.putExtra("orientation", j_orientation)
        log(f'ready to start intent {j_entrypoint} {j_orientation}')
        activity.startActivity(intent)
        log('activity started')
        System.exit(0)

    # @staticmethod
    # def stop_android_activity(log):
    #     """Stop any started PythonActivity.
    #     Args:
    #         log (callable): The log function accepting a message parameter.
    #     """
    #     log(f'Stopping PythonActivity {AndroidActivity._activity}')
    #     if AndroidActivity._activity:
    #         AndroidActivity._activity.finish()
    #         AndroidActivity._activity = None
