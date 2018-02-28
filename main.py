# -*- coding: utf-8 -*-


def run_entrypoint(entrypoint):
    import runpy
    runpy.run_path(
        entrypoint,
        run_name="__main__")


def run_launcher(tb=None):
    from launcher.app import Launcher
    Launcher().run()


def dispatch():
    try:
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        intent = activity.getIntent()
        entrypoint = intent.getStringExtra("entrypoint")
        if entrypoint is not None:
            try:
                run_entrypoint(entrypoint)
                return
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
