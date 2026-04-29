

# Import necessary PyQt6 widgets for GUI elements
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
import sys

# Import the BeckhoffController class which handles all communication with the Beckhoff device
from controller import BeckhoffController

class IOTestGui(QWidget):
    def __init__(self):
        super().__init__()
        # Set the window title
        self.setWindowTitle("Modular IO Test GUI")
        # Set the window size (x, y, width, height)
        self.setGeometry(100, 100, 900, 350)

        # Create the BeckhoffController instance for all I/O operations
        # This connects to the Beckhoff device at the given IP and port
        self.controller = BeckhoffController(ip="192.168.1.1", port=502)
        # If connection fails, show a popup error
        if not self.controller.connected:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Connection Error", "Could not connect to Beckhoff at 192.168.1.1:502")

        # Main vertical layout for the window
        layout = QVBoxLayout()

        # Lists to keep track of label and button widgets for outputs and inputs
        self.output_labels = []   # Output state display labels
        self.output_buttons = []  # Output toggle buttons
        self.input1_labels = []   # Input 9-16 state labels
        self.input1_buttons = []  # Input 9-16 read buttons
        self.input2_labels = []   # Input 17-24 state labels
        self.input2_buttons = []  # Input 17-24 read buttons


        # --- Row 1: Output controls (named outputs) ---
        from io_map import PINS
        output_names = [name for name, pin in PINS.items() if pin["type"] == "coil"]
        row1_labels = QHBoxLayout()
        row1_buttons = QHBoxLayout()
        for idx, name in enumerate(output_names):
            label = QLabel("-")
            label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            self.output_labels.append(label)
            row1_labels.addWidget(label)
            btn = QPushButton(f"Toggle {name}")
            self.output_buttons.append(btn)
            btn.clicked.connect(self._make_toggle_output(name, idx))
            row1_buttons.addWidget(btn)
        layout.addLayout(row1_labels)
        layout.addLayout(row1_buttons)

        # --- Row 2: Input controls (first 8 named inputs) ---
        input_names = [name for name, pin in PINS.items() if pin["type"] == "discrete_input"]
        row2_labels = QHBoxLayout()
        row2_buttons = QHBoxLayout()
        for idx, name in enumerate(input_names[:8]):
            label = QLabel("-")
            label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            self.input1_labels.append(label)
            row2_labels.addWidget(label)
            btn = QPushButton(f"Read {name}")
            self.input1_buttons.append(btn)
            btn.clicked.connect(self._make_read_input(name, label))
            row2_buttons.addWidget(btn)
        layout.addLayout(row2_labels)
        layout.addLayout(row2_buttons)

        # --- Row 3: Input controls (next 8 named inputs) ---
        row3_labels = QHBoxLayout()
        row3_buttons = QHBoxLayout()
        for idx, name in enumerate(input_names[8:]):
            label = QLabel("-")
            label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            self.input2_labels.append(label)
            row3_labels.addWidget(label)
            btn = QPushButton(f"Read {name}")
            self.input2_buttons.append(btn)
            btn.clicked.connect(self._make_read_input(name, label))
            row3_buttons.addWidget(btn)
        layout.addLayout(row3_labels)
        layout.addLayout(row3_buttons)

        # Set the main layout for the window
        self.setLayout(layout)

    # Returns a function that toggles the output by name
    def _make_toggle_output(self, name, idx):
        def toggle():
            try:
                current = self.controller.get_output(name)
                new_val = not current
                self.controller.set_output(name, new_val)
                self.output_labels[idx].setText("ON" if new_val else "OFF")
            except Exception as e:
                self.output_labels[idx].setText(f"ERR: {e}")
        return toggle


    # Returns a function that reads the input by name and updates the label
    def _make_read_input(self, name, label):
        def read():
            try:
                val = self.controller.read_input(name)
                label.setText("ON" if val else "OFF")
            except Exception as e:
                label.setText(f"ERR: {e}")
        return read


# Import Qt for alignment constants (not strictly needed here)
from PyQt6.QtCore import Qt


# This block runs if the script is executed directly (not imported)
if __name__ == "__main__":
    # Create the Qt application
    app = QApplication(sys.argv)
    # Create the main window
    window = IOTestGui()
    # Show the window
    window.show()
    # Start the Qt event loop (this keeps the window open)
    sys.exit(app.exec())
