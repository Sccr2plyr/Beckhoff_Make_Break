from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException


class BeckhoffController:
    def __init__(self, ip="192.168.1.1", port=502):
        self.ip = ip
        self.port = port
        self.timeout = 60
        self.client = ModbusTcpClient(self.ip, port=self.port, timeout=self.timeout)
        self.connected = self.client.connect()
        self.outputs = [False] * 8

    def reconnect(self):
        try:
            self.client.close()
        except Exception:
            pass

        self.client = ModbusTcpClient(self.ip, port=self.port, timeout=self.timeout)
        self.connected = self.client.connect()
        return self.connected

    def set_output(self, channel, state):
        self.outputs[channel] = state

    def apply_outputs(self):
        try:
            for i in range(8):
                self.client.write_coil(i, self.outputs[i])
        except ConnectionException:
            if not self.reconnect():
                raise
            for i in range(8):
                self.client.write_coil(i, self.outputs[i])

    def read_input(self, channel):
        try:
            rr = self.client.read_discrete_inputs(channel, count=1)
            if rr.isError():
                raise RuntimeError(f"Modbus error reading input {channel}: {rr}")
            return bool(rr.bits[0])
        except ConnectionException:
            if not self.reconnect():
                raise
            rr = self.client.read_discrete_inputs(channel, count=1)
            if rr.isError():
                raise RuntimeError(f"Modbus error reading input {channel}: {rr}")
            return bool(rr.bits[0])

    def read_output(self, channel):
        try:
            rr = self.client.read_coils(channel, count=1)
            if rr.isError():
                raise RuntimeError(f"Modbus error reading coil {channel}: {rr}")
            return bool(rr.bits[0])
        except ConnectionException:
            if not self.reconnect():
                raise
            rr = self.client.read_coils(channel, count=1)
            if rr.isError():
                raise RuntimeError(f"Modbus error reading coil {channel}: {rr}")
            return bool(rr.bits[0])

    def all_off(self):
        for i in range(8):
            self.outputs[i] = False
        self.apply_outputs()

    def close(self):
        try:
            self.all_off()
        except Exception:
            pass
        self.client.close()