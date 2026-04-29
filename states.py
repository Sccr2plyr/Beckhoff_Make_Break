import time
from enum import Enum, auto
from io_map import PINS

class SystemState(Enum):
    IDLE = auto()
    RUNNING = auto()
    EMERGENCY_STOP = auto()
    # Add more states as needed

class Safety_States:

    def __init__(self):
            # ... your existing code ...
            
            self.prev_input1 = [False] * 8
            self.prev_input2 = [False] * 8
            self.system_stopped = False  # safety latch

            self.poll_timer = QTimer()
            self.poll_timer.timeout.connect(self.poll_inputs)
            self.poll_timer.start(50)  # 50ms for safety-critical

    def poll_inputs(self):
        if self.system_stopped:
            return  # don't do anything until manually reset

        # Read all inputs first, THEN check conditions
        current1 = []
        current2 = []

        for i in range(8):
            try:
                val = self.controller.read_input(f"input{i+9}")
                current1.append(val)
                self.input1_labels[i].setText("ON" if val else "OFF")
            except Exception as e:
                self.input1_labels[i].setText(f"ERR: {e}")
                current1.append(False)

        for i in range(8):
            try:
                val = self.controller.read_input(f"input{i+17}")
                current2.append(val)
                self.input2_labels[i].setText("ON" if val else "OFF")
            except Exception as e:
                self.input2_labels[i].setText(f"ERR: {e}")
                current2.append(False)

        # Safety check — are any two inputs ON at the same time?
        all_inputs = current1 + current2
        active = [i for i, v in enumerate(all_inputs) if v]

        if len(active) >= 2:
            self.emergency_stop(active)
            return

        self.prev_input1 = current1
        self.prev_input2 = current2

    def emergency_stop(self, active_channels):
        self.system_stopped = True
        self.poll_timer.stop()  # stop polling immediately

        # Turn off ALL outputs
        for i in range(8):
            try:
                self.controller.set_output(f"output{i+1}", False)
                self.output_labels[i].setText("OFF")
            except Exception as e:
                print(f"Failed to turn off output{i+1}: {e}")

        # Disable all buttons
        for btn in self.output_buttons + self.input1_buttons + self.input2_buttons:
            btn.setEnabled(False)

        # Alert the user
        names = [f"input{i+9}" for i in active_channels]
        QMessageBox.critical(
            self,
            "SAFETY STOP",
            f"SYSTEM HALTED\n\nSimultaneous inputs detected: {', '.join(names)}\n\nAll outputs have been turned off.\nReset required to continue."
        )

    def reset_system(self):
        """Call this to allow restart after a safety stop"""
        self.system_stopped = False
        self.prev_input1 = [False] * 8
        self.prev_input2 = [False] * 8

        for btn in self.output_buttons + self.input1_buttons + self.input2_buttons:
            btn.setEnabled(True)

        self.poll_timer.start(50)


def _sleep_with_keepalive(controller, duration_ms, step_ms=1000):
    remaining_s = max(0.0, float(duration_ms) / 1000.0)
    step_s = max(0.1, float(step_ms) / 1000.0)

    while remaining_s > 0:
        chunk = min(step_s, remaining_s)
        time.sleep(chunk)
        # Re-apply current outputs to avoid long idle socket periods.
        controller.apply_outputs()
        remaining_s -= chunk

def off(controller):
    controller.all_off()

def handle_emergency(controller, reason):
    controller.all_off()
    print(f"EMERGENCY: {reason}")
    # You can add more actions here (e.g., logging, notifications)

def check_emergency_conditions(controller):
    # Example: check if both HX460A and HX460B are ON
    hx460a = controller.get_pin("hx460a")
    hx460b = controller.get_pin("hx460b")
    if hx460a and hx460b:
        return "Both HX460A and HX460B are ON"
    # Add more named pin checks here as needed
    return None

# Example usage in your state machine or polling loop:
# reason = check_emergency_conditions(controller)
# if reason:
#     handle_emergency(controller, reason)

