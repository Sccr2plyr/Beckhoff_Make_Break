import time
from controller import BeckhoffController
from statemachine import SafetyStateMachine, SystemState

def emergency_handler(reason):
    print(f"EMERGENCY: {reason}")

if __name__ == "__main__":
    controller = BeckhoffController()
    sm = SafetyStateMachine(controller, on_emergency=emergency_handler)
    print("System started. State machine running. Press Ctrl+C to exit.")
    last_state = None
    try:
        while True:
            sm.poll_inputs()
            if sm.state != last_state:
                print(f"Current state: {sm.state.name}")
                last_state = sm.state
            # If stuck in INITIALIZING, print error and stay in loop
            if sm.state == SystemState.INITIALIZING:
                cap1_ok = controller.get_pin("input2")
                cap2_ok = controller.get_pin("input3")
                if not (cap1_ok and cap2_ok):
                    print("Initialization failed: Cap 1 or Cap 2 is LOW. System remains in INITIALIZING state.")
            # No exit on fault or emergency; state machine will handle emergency pins
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting...")
    controller.close()