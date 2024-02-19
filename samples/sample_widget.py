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
