from states import SystemState, handle_emergency

class SafetyStateMachine:
    def __init__(self, controller, on_emergency=None):
        self.controller = controller
        self.state = SystemState.INITIALIZING
        self.on_emergency = on_emergency  # Optional callback for UI/message

    def poll_inputs(self):
        # --- State: INITIALIZING ---
        if self.state == SystemState.INITIALIZING:
            cap1_ok = self.controller.get_pin("input2")
            cap2_ok = self.controller.get_pin("input3")
            if cap1_ok and cap2_ok:
                self.transition_to(SystemState.RUNNING, reason="All caps OK, entering RUNNING")
            else:
                if not cap1_ok:
                    print("Cap 1 is LOW at startup. Not entering RUNNING state.")
                if not cap2_ok:
                    print("Cap 2 is LOW at startup. Not entering RUNNING state.")
            return
        # --- State: RUNNING ---
        if self.state == SystemState.RUNNING:
            self.controller.set_pin("output3", True)
            self.controller.set_pin("output5", True)
            # Cap 1 fault
            if not self.controller.get_pin("input2"):
                self.transition_to(SystemState.EMERGENCY_STOP, reason="Cap 1 fault: input2 is LOW")
                return
            # Cap 2 fault
            if not self.controller.get_pin("input3"):
                self.transition_to(SystemState.EMERGENCY_STOP, reason="Cap 2 fault: input3 is LOW")
                return
        # --- State: IDLE ---
        elif self.state == SystemState.IDLE:
            pass
        # --- Emergency check (always check for emergency) ---
        hx460a = self.controller.get_pin("hx460a")
        hx460b = self.controller.get_pin("hx460b")
        if hx460a and hx460b:
            self.transition_to(SystemState.EMERGENCY_STOP, reason="Both HX460s are ON")
            return

    def transition_to(self, new_state, reason=None):
        if self.state == new_state:
            return
        self.state = new_state
        if new_state == SystemState.EMERGENCY_STOP:
            handle_emergency(self.controller, reason)
            if self.on_emergency:
                self.on_emergency(reason)
        elif new_state == SystemState.RUNNING:
            print("Transitioned to RUNNING: outputs 13 and 5 ON")
        # Add more state entry handlers as needed
