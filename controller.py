# Import pymodbus for Modbus TCP communication
from pymodbus.client import ModbusTcpClient
# Import exception for handling connection errors (not used directly here)
from pymodbus.exceptions import ConnectionException
# Load PINS from io_map.json
import json
import os
with open(os.path.join(os.path.dirname(__file__), "io_map.json"), "r") as f:
    PINS = json.load(f)

# --- Optional Helper Classes (not used directly in GUI, but useful for modular code) ---


# --- Main Controller Class Used by the GUI ---

class BeckhoffController:
        
    """
    BeckhoffController: Main class for managing connection and I/O with the Beckhoff device.
    This is the class used by the GUI for all operations.
    """

    def __init__(self, ip="192.168.1.1", port=502):
        # Store connection parameters
        self.ip = ip
        self.port = port
        self.timeout = 60
        # Create the Modbus TCP client
        self.client = ModbusTcpClient(self.ip, port=self.port, timeout=self.timeout)
        # Attempt to connect to the Beckhoff device
        self.connected = self.client.connect()
        # Track output states (not strictly needed for Modbus, but kept for compatibility)
        self.outputs = [False] * 8

    # --- Generic pin access using PINS config ---
    def set_pin(self, name, value):
        """
        Set any output pin (coil) by name. Example: set_pin('output1', True)
        """
        pin = PINS.get(name)
        if not pin or pin["type"] != "coil":
            raise ValueError(f"Pin {name} is not a valid output (coil)")
        self.client.write_coil(pin["address"], bool(value))

    def get_pin(self, name):
        """
        Read any pin (output or input) by name. Example: get_pin('input9')
        """
        pin = PINS.get(name)
        if not pin:
            raise ValueError(f"Pin {name} not found in config")
        if pin["type"] == "coil":
            result = self.client.read_coils(address=pin["address"], count=1)
        elif pin["type"] == "discrete_input":
            result = self.client.read_discrete_inputs(address=pin["address"], count=1)
        else:
            raise ValueError(f"Unknown pin type for {name}")
        if hasattr(result, 'bits'):
            return bool(result.bits[0])
        return False
    
    
    def reconnect(self):
        """Reconnect to the Beckhoff device."""
        try:
            self.client.close()
        except Exception:
            pass
        self.client = ModbusTcpClient(self.ip, port=self.port, timeout=self.timeout)
        self.connected = self.client.connect()
        return self.connected

    # Close the connection and turn all outputs off
    def close(self):
        try:
            self.all_off()
        except Exception:
            pass
        self.client.close()


    # Legacy methods for compatibility (optional, can be removed if not used)
    def set_output(self, name_or_index, value):
        if isinstance(name_or_index, int):
            name = f"output{name_or_index+1}"
        else:
            name = name_or_index
        self.set_pin(name, value)


    def get_output(self, name_or_index):
        if isinstance(name_or_index, int):
            name = f"output{name_or_index+1}"
        else:
            name = name_or_index
        return self.get_pin(name)


    def read_input(self, name_or_index):
        if isinstance(name_or_index, int):
            name = f"input{name_or_index+9}"
        else:
            name = name_or_index
        return self.get_pin(name)

    # Turn all outputs off (set all coils to False)
    def all_off(self):
        for i in range(8):
            self.set_output(i, False)