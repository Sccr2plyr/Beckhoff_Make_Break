import time


def _sleep_with_keepalive(controller, duration_ms, step_ms=1000):
    remaining_s = max(0.0, float(duration_ms) / 1000.0)
    step_s = max(0.1, float(step_ms) / 1000.0)

    while remaining_s > 0:
        chunk = min(step_s, remaining_s)
        time.sleep(chunk)
        # Re-apply current outputs to avoid long idle socket periods.
        controller.apply_outputs()
        remaining_s -= chunk

def armed(controller):
    controller.all_off()
    controller.set_output(0, True)   # output 0 on
    controller.apply_outputs()

def isolate(controller):
    # For testing, we'll just toggle output 1 on and off with user-defined timings
    on_time = input("Type On Time in milliseconds: ")
    off_time = input("Type Off Time in milliseconds: ")

    # In a real system, this would likely involve more complex logic to isolate specific components
    controller.set_output(1, True)   # output 1 on
    controller.apply_outputs()

    # Wait for the specified on time, then turn off the output and wait for the off time
    _sleep_with_keepalive(controller, on_time)
    controller.set_output(1, False)   # output 1 off
    controller.apply_outputs()
    _sleep_with_keepalive(controller, off_time)
    controller.all_off()

def off(controller):
    controller.all_off()

