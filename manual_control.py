import tkinter as tk
from tkinter import ttk

from controller import BeckhoffController


class PulseControlGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Beckhoff Pulse Control")
        self.root.geometry("500x340")
        self.root.resizable(False, False)

        self.controller = BeckhoffController()
        self.pulse_running = False
        self.pulse_off_timer = None
        self.pulse_done_timer = None
        self.heartbeat_timer = None
        self.safety_timer = None
        self.shutdown_latched = False

        self.on_ms_var = tk.StringVar(value="500")
        self.off_ms_var = tk.StringVar(value="500")
        self.trip_channels_var = tk.StringVar(value="0")
        self.shutdown_on_trip_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()
        self._heartbeat()
        self._monitor_safety()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Output 1 Pulse (coil index 1)").grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(frame, text="On Time (ms)").grid(row=1, column=0, sticky="w", pady=(12, 4))
        ttk.Entry(frame, textvariable=self.on_ms_var, width=18).grid(row=1, column=1, sticky="w", pady=(12, 4))

        ttk.Label(frame, text="Off Time (ms)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.off_ms_var, width=18).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Trip Inputs (0-based, comma-separated)").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.trip_channels_var, width=18).grid(row=3, column=1, sticky="w", pady=4)

        ttk.Checkbutton(
            frame,
            text="Close app on safety trip",
            variable=self.shutdown_on_trip_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 8))

        ttk.Button(frame, text="Run Pulse", command=self.run_pulse).grid(row=5, column=0, sticky="we", pady=(10, 6))
        ttk.Button(frame, text="Arm", command=self.arm).grid(row=5, column=1, sticky="we", pady=(10, 6))

        ttk.Button(frame, text="All Off", command=self.all_off).grid(row=6, column=0, sticky="we", pady=6)
        ttk.Button(frame, text="Reconnect", command=self.reconnect).grid(row=6, column=1, sticky="we", pady=6)

        ttk.Separator(frame, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="we", pady=(8, 8))
        ttk.Label(frame, textvariable=self.status_var, wraplength=460).grid(row=8, column=0, columnspan=2, sticky="w")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def _parse_non_negative_ms(self, value):
        ms = int(value)
        if ms < 0:
            raise ValueError("Time must be >= 0")
        return ms

    def _parse_trip_channels(self):
        text = self.trip_channels_var.get().strip()
        if not text:
            return []

        channels = []
        for part in text.split(","):
            value = int(part.strip())
            if value < 0:
                raise ValueError("Trip channels must be >= 0")
            channels.append(value)
        return channels

    def _cancel_pulse_timers(self):
        for timer_name in ("pulse_off_timer", "pulse_done_timer"):
            timer = getattr(self, timer_name)
            if timer is not None:
                self.root.after_cancel(timer)
                setattr(self, timer_name, None)
        self.pulse_running = False

    def _trigger_safety_shutdown(self, reason):
        if self.shutdown_latched:
            return

        self.shutdown_latched = True
        self._cancel_pulse_timers()

        try:
            self.controller.all_off()
        except Exception:
            pass

        self.status_var.set(f"SAFETY TRIP: {reason}. Outputs forced OFF")

        if self.shutdown_on_trip_var.get():
            self.root.after(150, self.on_close)

    def run_pulse(self):
        if self.shutdown_latched:
            self.status_var.set("Safety trip latched. Restart app to continue")
            return

        if self.pulse_running:
            self.status_var.set("Pulse already running")
            return

        try:
            on_ms = self._parse_non_negative_ms(self.on_ms_var.get().strip())
            off_ms = self._parse_non_negative_ms(self.off_ms_var.get().strip())
        except ValueError:
            self.status_var.set("Invalid input: use integer milliseconds")
            return

        try:
            self.controller.set_output(1, True)
            self.controller.apply_outputs()
        except Exception as exc:
            self.status_var.set(f"Write failed: {exc}")
            return

        self.pulse_running = True
        self.status_var.set(f"Output 1 ON for {on_ms} ms")
        self.pulse_off_timer = self.root.after(on_ms, lambda: self._pulse_turn_off(off_ms))

    def _pulse_turn_off(self, off_ms):
        self.pulse_off_timer = None
        try:
            self.controller.set_output(1, False)
            self.controller.apply_outputs()
        except Exception as exc:
            self.status_var.set(f"Write failed: {exc}")
            self.pulse_running = False
            return

        self.status_var.set(f"Output 1 OFF for {off_ms} ms")
        self.pulse_done_timer = self.root.after(off_ms, self._pulse_done)

    def _pulse_done(self):
        self.pulse_done_timer = None
        self.pulse_running = False
        self.status_var.set("Pulse complete")

    def arm(self):
        if self.shutdown_latched:
            self.status_var.set("Safety trip latched. Restart app to continue")
            return

        try:
            self.controller.all_off()
            self.controller.set_output(0, True)
            self.controller.apply_outputs()
            self.status_var.set("Armed: Output 0 ON")
        except Exception as exc:
            self.status_var.set(f"Arm failed: {exc}")

    def all_off(self):
        try:
            self.controller.all_off()
            self._cancel_pulse_timers()
            self.status_var.set("All outputs OFF")
        except Exception as exc:
            self.status_var.set(f"All-off failed: {exc}")

    def reconnect(self):
        ok = self.controller.reconnect()
        if ok:
            self.status_var.set("Reconnected")
        else:
            self.status_var.set("Reconnect failed")

    def _heartbeat(self):
        if self.shutdown_latched:
            return

        try:
            self.controller.apply_outputs()
        except Exception:
            # Keep UI responsive even during temporary PLC comm failures.
            pass
        self.heartbeat_timer = self.root.after(1000, self._heartbeat)

    def _monitor_safety(self):
        if self.shutdown_latched:
            return

        try:
            trip_channels = self._parse_trip_channels()
        except ValueError as exc:
            self._trigger_safety_shutdown(str(exc))
            return

        try:
            for channel in trip_channels:
                if self.controller.read_input(channel):
                    self._trigger_safety_shutdown(f"Input {channel} is ON")
                    return
        except Exception as exc:
            self._trigger_safety_shutdown(f"Monitor read failed ({exc})")
            return

        self.safety_timer = self.root.after(200, self._monitor_safety)

    def on_close(self):
        for timer in (self.pulse_off_timer, self.pulse_done_timer, self.heartbeat_timer, self.safety_timer):
            if timer is not None:
                self.root.after_cancel(timer)
        self.controller.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    PulseControlGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()