import time
from controller import BeckhoffController
from statemachine import SafetyStateMachine, SystemState

def emergency_handler(reason):
    print(f"EMERGENCY: {reason}")

if __name__ == "__main__":
    controller = BeckhoffController()
    sm = SafetyStateMachine(controller, on_emergency=emergency_handler)
    print("System started. State machine running. Press Ctrl+C to exit.")
    try:
        while True:
            sm.poll_inputs()
            print(f"Current state: {sm.state.name}")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
    controller.close()