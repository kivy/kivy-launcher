# -*- coding: utf-8 -*-

import os
import re
import hashlib
import requests
import zipfile
from kivy.app import App
from kivy.utils import platform
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty
from glob import glob
from os.path import dirname, join, exists, realpath
import traceback

KIVYLAUNCHER_PATHS = os.environ.get("KIVYLAUNCHER_PATHS")


class Importer(object):
    URI = None
    NAME = None
    ICON = None

    @classmethod
    def match_uri(cls, uri):
        return re.match(cls.URI, uri) is not None

    def __init__(self, uri):
        self.uri = uri
        super(Importer, self).__init__()

    def retrieve_metadata(self):
        self.metadata = {
            "name": "Unknown",
            "author": "Unknown"
        }

    def get_id(self):
        return hashlib.sha224(self.uri.encode("utf-8")).hexdigest()

    def get_name(self):
        return self.metadata["name"]

    def get_author(self):
        return self.metadata["author"]


class GitHubGistImporter(Importer):
    URI = "https://gist.github.com/([^\/]+)/([a-f0-9]+)"
    NAME = "GitHub Gist"
    ICON = "G"

    def retrieve_metadata(self):
        gist_id = re.match(self.URI, self.uri).group(2)
        req = requests.get(
            "https://api.github.com/gists/{}".format(gist_id))
        req.raise_for_status()
        data = req.json()
        author = data["owner"]["login"]
        name = data["description"]
        if not name:
            if len(data["files"]):
                name = list(data["files"].keys())[0]
            else:
                name = data["id"]
        self.metadata = {
            "name": name,
            "author": author
        }

    def get_download_url(self):
        return self.uri + "/archive/master.zip"


class GitHubImporter(Importer):
    URI = "https://github.com/([^\/]+)/(.*)"
    NAME = "GitHub"
    ICON = "G"

    def retrieve_metadata(self):
        pass

    def get_download_url(self):
        return self.uri + "/archive/master.zip"


class AddForm(Factory.GridLayout):
    form_ok = BooleanProperty(False)

    def validate_uri(self, text):
        self.form_ok = App.get_running_app().validate_uri(text)

    def add(self, uri):
        App.get_running_app().add_manual_entry(uri)


class LauncherContent(Factory.GridLayout):
    pass


class Launcher(App):
    IMPORTERS = [
        GitHubGistImporter,
        GitHubImporter
    ]
    form_index = NumericProperty(0)

    def build(self):
        if platform == "android":
            self.store_path = "/sdcard/kivy/remotes/"
        else:
            self.store_path = "./remotes/"
        self.ensure_directory(self.store_path)

        self.paths = [
            "/sdcard/kivy",
            self.store_path
        ]
        if KIVYLAUNCHER_PATHS:
            self.paths.extend(KIVYLAUNCHER_PATHS.split(","))

        Builder.load_file("data/launcher.kv")
        self.root = LauncherContent()
        self.refresh_entries()

    def refresh_entries(self):
        data = []
        for entry in self.find_entries(paths=self.paths):
            can_refresh = entry.get("uri") is not None
            can_run = entry.get("entrypoint") not in (None, "")
            data.append({
                "data_can_refresh": can_refresh,
                "data_can_run": can_run,
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
        if data.get("entrypoint") is None:
            data["entrypoint"] = join(dirname(filename), "main.py")
        if data.get("path") is None:
            data["path"] = dirname(data["entrypoint"])
        data["project_path"] = dirname(filename)
        icon = join(data["path"], "icon.png")
        if exists(icon):
            data["icon"] = icon
        return data

    def get_importer_from_uri(self, uri):
        for importer in self.IMPORTERS:
            if importer.match_uri(uri):
                return importer

    def validate_uri(self, uri):
        return self.get_importer_from_uri(uri) is not None

    def add_manual_entry(self, uri):
        cls = self.get_importer_from_uri(uri)
        if not cls:
            return

        importer = cls(uri)
        importer.retrieve_metadata()

        # check if the directory already exists
        project_dir = join(self.store_path, importer.get_id())
        self.ensure_directory(project_dir)

        android_txt = join(project_dir, "android.txt")
        if not exists(android_txt):
            content = "\n".join([
                "title={}".format(importer.get_name()),
                "author={}".format(importer.get_author()),
                "orientation=portrait",
                "entrypoint=",
                "uri={}".format(importer.uri),
                ""
            ])
            with open(android_txt, "w") as fd:
                fd.write(content)

        self.refresh_entries()
        self.form_index = 0

    def delete_entry(self, entry):
        import shutil
        shutil.rmtree(entry["project_path"])
        self.refresh_entries()

    def refresh_entry(self, entry):
        cls = self.get_importer_from_uri(entry["uri"])
        if not cls:
            return
        importer = cls(entry["uri"])
        url = importer.get_download_url()
        req = requests.get(url)
        req.raise_for_status()

        # save to master.zip
        project_path = entry["project_path"]
        master_zip = join(project_path, "master.zip")
        with open(master_zip, "wb") as fd:
            fd.write(req.content)

        # extract directory
        extract_dir = join(project_path, "extract")
        self.ensure_directory(extract_dir)

        # now unzip
        ref = zipfile.ZipFile(master_zip, "r")
        ref.extractall(extract_dir)
        ref.close()

        # resolve entrypoint
        py_files = list(self.find_py_files(extract_dir))
        print("Python files found:")
        print(py_files)

        entrypoint = None
        print("Entrypoint: search main.py")
        for filename in py_files:
            if filename.endswith("main.py"):
                entrypoint = filename
                break

        if not entrypoint:
            print("Entrypoint: fallback, search common pattern")
            for filename in py_files:
                with open(filename) as fd:
                    data = fd.read()
                    found = False
                    # search some common pattern
                    if ").run()" in data:
                        found = True
                    elif "runTouchApp(" in data:
                        found = True
                    if found:
                        entrypoint = filename
                        break

        if not entrypoint:
            print("Entrypoint: fallback, take first files")
            if py_files:
                entrypoint = py_files[0]

        if not entrypoint:
            print("No valid entrypoint found, abort")
            return

        # update android_txt
        if entrypoint.startswith("project_path"):
            entrypoint = entrypoint.replace(realpath(project_path), "")
            if entrypoint.startswith("/"):
                entrypoint = entrypoint[1:]

        print("Entrypoint: set to {}".format(entrypoint))
        print("Entrypoint: update android.txt")
        android_txt = join(project_path, "android.txt")
        with open(android_txt, "r") as fd:
            data = fd.read()
        data = data.replace(
            "entrypoint=\n", "entrypoint={}\n".format(entrypoint))
        data = data.replace(
            "path=\n", "path={}\n".format(dirname(entrypoint)))
        with open(android_txt, "w") as fd:
            fd.write(data)
        print("DONE!")
        print(data)

        self.refresh_entries()

    def find_py_files(self, directory):
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(".py"):
                    yield realpath(join(dirpath, filename))

    def ensure_directory(self, directory):
        if not exists(directory):
            os.makedirs(directory)

    def start_activity(self, entry):
        if platform == "android":
            self.start_android_activity(entry)
        else:
            self.start_desktop_activity(entry)

    def start_desktop_activity(self, entry):
        entrypoint = entry["entrypoint"]
        import sys
        from subprocess import Popen
        cmd = Popen([sys.executable, entrypoint])
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
