#!/usr/bin/env python3
"""Reporte Ecosistema SDC — fullscreen WebKit window on external HDMI monitor."""
import subprocess
import sys

sys.path.insert(0, '/usr/lib/python3/dist-packages')
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import GLib, Gtk, WebKit2

REPORT_URL = "http://localhost:5174/static/reporte-ecosistema.html"
MONITOR_X = 1366
MONITOR_Y = 0
MONITOR_W = 1920
MONITOR_H = 1080

class ReporteKiosk:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("SDC — Ecosystem Report")
        self.window.set_default_size(MONITOR_W, MONITOR_H)
        self.window.set_position(Gtk.WindowPosition.NONE)
        self.window.connect("destroy", Gtk.main_quit)
        self.window.fullscreen()

        webview = WebKit2.WebView()
        settings = webview.get_settings()
        settings.set_property("enable-developer-extras", False)
        settings.set_property("enable-javascript", True)
        webview.load_uri(REPORT_URL)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(webview)
        self.window.add(scrolled)

        GLib.timeout_add_seconds(300, lambda: webview.reload() or True)

    def run(self):
        self.window.show_all()
        GLib.timeout_add(500, self._move_to_hdmi)
        Gtk.main()

    def _move_to_hdmi(self):
        try:
            subprocess.run(
                ["xdotool", "search", "--name", "SDC", "windowmove", str(MONITOR_X), str(MONITOR_Y)],
                timeout=3, capture_output=True
            )
            subprocess.run(
                ["xdotool", "search", "--name", "SDC", "windowsize", str(MONITOR_W), str(MONITOR_H)],
                timeout=3, capture_output=True
            )
        except Exception:
            pass
        return False

if __name__ == "__main__":
    ReporteKiosk().run()
