from states import SystemState, handle_emergency

class SafetyStateMachine:
    def __init__(self, controller, on_emergency=None):
        self.controller = controller
        self.state = SystemState.IDLE
        self.on_emergency = on_emergency  # Optional callback for UI/message

    def poll_inputs(self):
        # Example: check for HX460A and HX460B both ON
        hx460a = self.controller.get_pin("hx460a")
        hx460b = self.controller.get_pin("hx460b")
        # ... check other inputs as needed

        if hx460a and hx460b:
            self.transition_to(SystemState.EMERGENCY_STOP, reason="Both HX460s are ON")
            return

        # Add more state checks and transitions here

    def transition_to(self, new_state, reason=None):
        if self.state == new_state:
            return
        self.state = new_state
        if new_state == SystemState.EMERGENCY_STOP:
            handle_emergency(self.controller, reason)
            if self.on_emergency:
                self.on_emergency(reason)
        # Add more state entry handlers as needed
