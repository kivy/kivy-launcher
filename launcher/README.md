# Kivy Launcher

(work in progress, not yet published on Google Play)

This is a reboot of the previously pygame/kivy launcher, implemented in Java in Python for android. It was barely maintainable, and with the rewrite of the new Python for android, it was lost.

This version aimed to provide a replacement for the launcher, but works also on desktop, on Python 2 or 3.

Anybody can clone the repo, add the dependencies we would not provide by default, and recompile it.

## How it works

Follow the guide the same as before: https://kivy.org/docs/guide/packaging-android.html#packaging-your-application-for-the-kivy-launcher

Then just start the launcher, you should see your application listed, then press play.

## Works

- Provide a simple UI to discover and start another app
- Start another main.py as a `__name__ == '__main__'`
- Reduce to the minimum the overhead of the launcher to launch another app

## Ideas

- Support landscape / portrait
- Act as a server to just launch any Kivy-based app from desktop to mobile
- Ability to configure multiple paths to look for applications
- Different ordering: by name, last updated, size
- Add tiny icon to show what application orientation is
- Allow to change multiple configuration token / environemnt (like different density/dpi to simulate other screens)
- Support for application without "android.txt"
