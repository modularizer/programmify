import os
import signal
import subprocess
import threading
import time
from pathlib import Path

from PyQt5 import QtWidgets, QtGui, QtCore

from programmify.programmify import ProgrammifyWidget


class ProcessThread(QtCore.QThread):
    output_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    pid_signal = QtCore.pyqtSignal(int)
    exit_signal = QtCore.pyqtSignal(int)

    def __init__(self, cmd, cwd=None, parent=None):
        super(ProcessThread, self).__init__(parent)
        self.cmd = cmd
        self.cwd = cwd

    def run(self):
        self.process = subprocess.Popen(self.cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
        self.pid_signal.emit(self.process.pid)
        exit_code = None
        while True:
            output = self.process.stdout.readline()
            exit_code = self.process.poll()
            if (not output) and (exit_code is not None):
                break
            if output:
                self.output_signal.emit(output.strip().decode())
        # Handle stderr in a similar fashion if needed
        # if it existed with an error code
        if self.process.poll() != 0:
            error = self.process.stderr.read()
            self.error_signal.emit(error.strip().decode())
        self.exit_signal.emit(exit_code)


class SubprocessWidget(ProgrammifyWidget):
    def __init__(self, cmd, cwd=Path.cwd(), stay_open=False, name: str = None, icon: str = None, **kw):
        if isinstance(cmd, str):
            cmd = [v.strip() for v in cmd.split(" ") if v.strip()]
        self.cmd = cmd
        self.cwd = cwd
        self.pid = None
        self.exit_code = None
        self.stay_open = stay_open
        super().__init__(name, icon, **kw)

    def setupUI(self):
        # Create a layout
        layout = QtWidgets.QVBoxLayout(self)

        # Dark mode colors
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        self.setPalette(palette)

        # add a banner with the PID and process name
        self.banner = QtWidgets.QLabel(self)

        # add space between the banner and the output display
        layout.addWidget(self.banner)

        # Create a QTextEdit widget for displaying output and error
        self.output_display = QtWidgets.QTextEdit(self)
        self.output_display.setStyleSheet("background-color: #2b2b2b; color: white;")
        layout.addWidget(self.output_display)

        # Create a stop button
        self.stop_button = QtWidgets.QPushButton('Stop (SIGINT)', self)
        self.stop_button.setDisabled(True)
        self.stop_button.clicked.connect(self.interrupt_process)
        layout.addWidget(self.stop_button)

        # Set the layout on the QWidget
        self.setLayout(layout)

        # Instantiate and start ProcessThread
        self.process_thread = ProcessThread(self.cmd, self.cwd)
        self.process_thread.output_signal.connect(self.handle_stdout)
        self.process_thread.error_signal.connect(self.handle_stderr)
        self.process_thread.pid_signal.connect(self.handle_pid)
        self.process_thread.exit_signal.connect(self.handle_exit)
        self.process_thread.start()

    def handle_stdout(self, data):
        # Add data to the QTextEdit widget
        self.output_display.append(data)

    def handle_stderr(self, error):
        # Add error to the QTextEdit widget
        self.output_display.append(error)

    def handle_pid(self, pid):
        self.pid = pid
        self.stop_button.setDisabled(False)
        self.banner.setText(f'{self.name} (PID#{self.pid})')

    def handle_exit(self, exit_code):
        self.exit_code = exit_code
        self.stop_button.setText("Process Error" if exit_code else "Process finished")
        self.stop_button.setDisabled(True)
        if not self.stay_open and not exit_code:
            self.close()

    def interrupt_process(self):
        # send sigint to process using the os module
        os.kill(self.pid, signal.SIGINT)
        self.output_display.append('<SIGINT sent to process>')
        self.stop_button.setText("Stop (SIGTERM)")
        self.stop_button.clicked.disconnect(self.interrupt_process)
        self.stop_button.clicked.connect(self.terminate_process)

    def terminate_process(self):
        # send sigterm to process
        os.kill(self.pid, signal.SIGTERM)
        self.output_display.append('<SIGTERM sent to process>')
        self.stop_button.setText("Stop (SIGKILL)")
        self.stop_button.clicked.disconnect(self.terminate_process)
        self.stop_button.clicked.connect(self.kill_process)

    def kill_process(self):
        # send sigkill to process
        os.kill(self.pid, signal.SIGKILL)
        self.output_display.append('<SIGKILL sent to process>')
        self.stop_button.setText("Unable to stop")
        self.stop_button.setDisabled(True)

    def start_process(self):
        print(f"Starting process: {self.cmd}")
        self.process = subprocess.Popen(self.cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
        self.banner.setText(f'{self.name} (PID#{self.process.pid})')
        while True:
            output = self.process.stdout.readline()
            if (not output) and (self.process.poll() is not None):
                break
            if output:
                self.handle_stdout(output.strip().decode())
        self.stop_button.setText("Process finished")
        self.stop_button.setDisabled(True)
        while True:
            error = self.process.stderr.readline()
            if (not error):
                break
            if error:
                self.handle_stderr(error.strip().decode())

    @classmethod
    def run(cls, cmd, **kw):
        app = QtWidgets.QApplication([])
        widget = cls(cmd, **kw)
        widget.show()
        app.exec_()


def sample(start, stop, interval=1):
    for i in range(start, stop):
        print(i)
        time.sleep(interval)


if __name__ == '__main__':
    import sys

    if sys.argv[1:]:
        start = int(sys.argv[1])
        stop = int(sys.argv[2])
        interval = int(sys.argv[3])
        sample(start, stop, interval)
    else:
        SubprocessWidget.run(cmd=[sys.executable, __file__, '1000', '1005', '1'])