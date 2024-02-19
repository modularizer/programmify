from programmify import ProgrammifyMainWindow


class MyWindow(ProgrammifyMainWindow):
    def setupUI(self):
        # Example: Setup a simple menu bar with one menu
        menu_bar = self.menuBar()  # QMainWindow's menu bar
        file_menu = menu_bar.addMenu("&File")

        # Example: Add an action to the File menu
        exit_action = file_menu.addAction("&Exit")
        exit_action.triggered.connect(self.close)  # Connect the action to close the QMainWindow


if __name__ == '__main__':
    MyWindow.run(name="MyWindow")
