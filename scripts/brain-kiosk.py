#!/usr/bin/env python3
"""JARVIS Command Center Kiosk — fullscreen WebKit window on external monitor."""
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import GLib, Gtk, WebKit2

DASHBOARD_URL = "http://localhost:5174/api/brain/dashboard"
MONITOR_X = 1366  # External monitor starts here
MONITOR_Y = 0
MONITOR_W = 1920
MONITOR_H = 1080

class BrainKiosk:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("JARVIS Command Center")
        self.window.set_default_size(MONITOR_W, MONITOR_H)
        self.window.move(MONITOR_X, MONITOR_Y)
        self.window.set_position(Gtk.WindowPosition.NONE)
        self.window.connect("destroy", Gtk.main_quit)
        self.window.fullscreen()

        # WebView
        webview = WebKit2.WebView()
        settings = webview.get_settings()
        settings.set_property("enable-developer-extras", False)
        settings.set_property("enable-javascript", True)
        webview.load_uri(DASHBOARD_URL)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(webview)
        self.window.add(scrolled)

        # Auto-refresh every 5 minutes
        GLib.timeout_add_seconds(300, lambda: webview.reload() or True)

    def run(self):
        self.window.show_all()
        Gtk.main()

if __name__ == "__main__":
    BrainKiosk().run()
