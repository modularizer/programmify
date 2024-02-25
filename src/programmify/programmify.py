import sys
from functools import wraps
from pathlib import Path
import setproctitle

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow

from programmify.detect import detect_icon
from programmify.png2ico import png_to_ico
from programmify.autoargparser import autoargparser

default_mode = "window"


class Programmify:
    def __init__(self, name: str = None, icon: str = None, **kwargs):
        """Create a new Programmify window.

        Args:
            name (str, optional): The name of the program. Defaults to the class name.
            icon (str, optional): The path to the icon file. Defaults to attempting to detect the icon in the working directory.
        """
        if name is None:
            name = self.__class__.__name__
        if icon is None:
            icon = detect_icon()
        super().__init__(**kwargs)
        self.trayIcon = QtWidgets.QSystemTrayIcon(self)
        self.name = self.set_name(name)
        self.icon, self.trayIcon, self.icon_path = self.set_icon(icon)
        self.setupUI()

    def setupUI(self):
        pass

    def set_icon(self, icon_path: str):
        if not icon_path:
            return None, None, None
        if not Path(icon_path).exists():
            raise FileNotFoundError(f"Icon file not found: {icon_path}")
        if icon_path.endswith(".png"):
            icon_path = png_to_ico(icon_path)
        self.icon_path = str(Path(icon_path).resolve())
        self.icon = QtGui.QIcon(self.icon_path)
        self.setWindowIcon(self.icon)
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.setVisible(True)
        return self.icon, self.trayIcon, self.icon_path

    def set_name(self, title: str):
        self.name = title
        if title:
            self.setWindowTitle(title)
            if self.trayIcon:
                self.trayIcon.setToolTip(title)
            setproctitle.setproctitle(title)
        return self.name

    @classmethod
    def run(cls, *args, **kwargs):
        print(f"Running {cls.__name__}")
        app = QtWidgets.QApplication(sys.argv)
        window = cls(*args, **kwargs)
        window.show()
        sys.exit(app.exec_())


@autoargparser
class ProgrammifyWidget(Programmify, QtWidgets.QWidget):
    pass


class ProgrammifyMainWindow(Programmify, QMainWindow):
    pass


def main():
    if "--window" in sys.argv:
        sys.argv.remove("--window")
        mode = "window"
    elif "--widget" in sys.argv:
        sys.argv.remove("--widget")
        mode = "widget"
    else:
        mode = default_mode
    cls = ProgrammifyMainWindow if mode == "window" else ProgrammifyWidget
    return autoargparser(cls).run()


if __name__ == '__main__':
    main()
