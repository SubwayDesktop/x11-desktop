#!/usr/bin/python3


import os
import sys
import json
import dbus
import dbus.service
import dbus.mainloop.glib
from PySide.QtCore import *
from PySide.QtGui import *


CONFIG_DIR = os.path.expanduser('~/.config/subway/')
CONFIG_FILE = CONFIG_DIR + 'x11-desktop'


desktop = None


class Desktop(QWidget):
    wallpaper = None

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_X11NetWmWindowTypeDesktop)
        self.resize(QApplication.desktop().size())

    def draw_wallpaper(self):
        painter = QPainter(self)
        image = self.wallpaper
        if image:
            painter.drawImage(self.geometry(), image, image.rect())
        else:
            painter.fillRect(self.geometry(), Qt.black)

    def update_wallpaper(self, wallpaper_file):
        self.wallpaper = QImage(wallpaper_file)
        self.repaint(self.geometry())

    def paintEvent(self, ev):
        self.draw_wallpaper()


class Adaptor(dbus.service.Object):
    def __init__(self, name, session):
        dbus.service.Object.__init__(self, name, session)

    @dbus.service.method('org.subwaydesktop.desktop',
                         in_signature='s', out_signature='')
    def set_wallpaper(self, wallpaper_file):
        global desktop
        desktop.update_wallpaper(wallpaper_file)
        write_config(wallpaper_file)


def read_config():
    global desktop
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if os.path.exists(CONFIG_FILE):
        f = open(CONFIG_FILE, 'r')
        config = json.load(f)
        f.close()
        desktop.update_wallpaper(config['wallpaper'])


def write_config(wallpaper_file):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    f = open(CONFIG_FILE, 'w')
    json.dump({'wallpaper': wallpaper_file}, f)
    f.close()


def main():
    global desktop
    app = QApplication(sys.argv)
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName('org.subwaydesktop.desktop', session_bus)
    adaptor = Adaptor(session_bus, '/Desktop')
    desktop = Desktop(None)
    desktop.show()
    read_config()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
