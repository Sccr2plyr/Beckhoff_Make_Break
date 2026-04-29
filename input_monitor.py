
# Minimal input monitor for one channel using BeckhoffController
import time
from controller import BeckhoffController

controller = BeckhoffController()
channel =   8
try:
    while True:
        value = controller.read_input(channel)
        print(f"Input {channel}: {value}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    controller.close()
