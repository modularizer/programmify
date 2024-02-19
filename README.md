# Programmify
Quickly make a windows executable with a system tray icon and an configurable (read empty) PyQT5 window

![Sample Widget](https://raw.githubusercontent.com/modularizer/programmify/master/resources/full.png)

Task Manager
![Task Manager](https://raw.githubusercontent.com/modularizer/programmify/master/resources/task_manager.png)

**Yes! You can use your own icon**

### Features
* [x] Use your own icon
* [x] System tray icon (in task bar)
* [x] Window title (in window title bar)
* [x] Window icon (in window title bar)
* [x] Executable name (in File Explorer & Task Manager)
* [x] Executable file icon (in File Explorer & Task Manager)
* [x] PyQT Widget OR PyQT Main Window

### Support
* [x] Windows
* [ ] Linux
* [ ] Mac

<hr/> 

# Quickstart
### 1. Install
```commandline
pip install programmify
```
OR git clone and run `pip install .` in the project directory

### 2. Code
import and use either `ProgrammifyWidget` or `ProgrammifyMainWindow` from `programmify` in your script
```python
# samples/sample_widget.py
from PyQt5 import QtWidgets

from programmify import ProgrammifyWidget


class MyWidget(ProgrammifyWidget):
    def setupUI(self):
        # Create a layout
        layout = QtWidgets.QVBoxLayout(self)

        # Add a label
        label = QtWidgets.QLabel("Hello, Programmify!")
        layout.addWidget(label)

        # Add a button
        button = QtWidgets.QPushButton("Click Me")
        button.clicked.connect(self.on_button_clicked)  # Connect to a method to handle the click event
        layout.addWidget(button)

        # Set the layout on the QWidget
        self.setLayout(layout)

    def on_button_clicked(self):
        QtWidgets.QMessageBox.information(self, "Action", "Button was clicked!")


if __name__ == '__main__':
    MyWidget.run()
```

3. Build
```commandline
programmify samples/sample_widget.py
```
**Optional**: add a `favicon.ico` in your current working directory to use as the icon for the program

4. Run
```commandline
sample_widget
```

<hr/> 

## Usage:
```commandline
programmify testprogram.py --name testprogram --icon testicon.ico
```

### Advanced usage:
* `programmify --help` to see all options
* add `--show_cmd` to show the `pyinstaller` command that will be run instead of running it (useful for debugging)

```commandline
usage: programmify [-h] [--name NAME] [--dst DST] [--icon ICON] [--mode MODE] [--nocleanup] [--nopreclean] [--show_cmd] [--cmd CMD]
                   [--hidden_imports [HIDDEN_IMPORTS ...]] [--extra_files [EXTRA_FILES ...]] [--debug] [--args ...]
                   file

positional arguments:
  file                  File to build. If not specified, will try ... 
                            1. main.py in current working directory if found 
                            2. __main__.py 
                            3. the only .py file in the current working directory if only one is found (excluding __init__.py) 
                            4. if there is a src directory, will search in src and its subdirectories to find a single option 
                            5. if the above fails, will raise an error and you will need to specify the file to build.

options:
  -h, --help            show this help message and exit
  --name NAME           Program name. If not specified, the name of the either the file or its parent directory will be used.
  --dst DST             Destination directory for the built program
  --icon ICON           Path to a 16x16 .ico file. If not specified, will try to find favicon.ico or any other .ico or .png in the current working directory.      
  --mode MODE           Program mode: window or widget
  --nocleanup           Cleanup build files
  --nopreclean          Preclean build files
  --show_cmd            Show the command that will be run instead of running it
  --cmd CMD             Expert level: command to run instead of pyinstaller
  --hidden_imports [HIDDEN_IMPORTS ...]
                        Hidden imports
  --extra_files [EXTRA_FILES ...]
                        Extra files to include
  --debug               Does not run in windowed mode, instead shows the terminal and stdout
  --args ...            Additional arguments to pass to pyinstaller
```

<hr/>

### Other Installed Scripts
* `png2ico` to convert a `.png` to a `.ico` file
  * see `png2ico --help` for usage