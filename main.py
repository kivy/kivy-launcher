# -*- coding: utf-8 -*-


def run_entrypoint(entrypoint):
    import runpy
    import sys
    import os
    entrypoint_path = os.path.dirname(entrypoint)
    sys.path.append(os.path.realpath(entrypoint_path))
    runpy.run_path(
        entrypoint,
        run_name="__main__")


def run_launcher(tb=None):
    from launcher.app import Launcher
    Launcher().run()


def dispatch():
    import os

    # desktop launch
    print("dispathc!")
    entrypoint = os.environ.get("KIVYLAUNCHER_ENTRYPOINT")
    if entrypoint is not None:
        return run_entrypoint(entrypoint)

    # try android
    try:
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        intent = activity.getIntent()
        entrypoint = intent.getStringExtra("entrypoint")
        orientation = intent.getStringExtra("orientation")

        if orientation == "portrait":
            # SCREEN_ORIENTATION_PORTRAIT
            activity.setRequestedOrientation(0x1)
        elif orientation == "landscape":
            # SCREEN_ORIENTATION_LANDSCAPE
            activity.setRequestedOrientation(0x0)
        elif orientation == "sensor":
            # SCREEN_ORIENTATION_SENSOR
            activity.setRequestedOrientation(0x4)

        if entrypoint is not None:
            try:
                return run_entrypoint(entrypoint)
            except Exception:
                import traceback
                traceback.print_exc()
                return
    except Exception:
        import traceback
        traceback.print_exc()

    run_launcher()


if __name__ == "__main__":
    dispatch()
