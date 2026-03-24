import time
from controller import BeckhoffController
import states

controller = BeckhoffController()

try:
    print("System starting...")

    while True:
        user_input = input("Type 'arm' or 'off': ")

        if user_input == "arm":
            states.armed(controller)

        elif user_input == "iso":
            states.isolate(controller)

        elif user_input == "off":
            controller.all_off()

        # ALWAYS apply outputs (keeps watchdog happy)
        controller.apply_outputs()

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Stopping...")

controller.close()