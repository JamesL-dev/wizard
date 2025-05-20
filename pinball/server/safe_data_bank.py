from threading import Lock

# Wrapper class for safe, thread-locked access to a Modbus data bank
class SafeDataBank:
    def __init__(self, data_bank):
        self.data_bank = data_bank
        self.lock = Lock()

    def get_coils(self, address, count):
        with self.lock:
            return self.data_bank.get_coils(address, count)

    def set_coils(self, address, values):
        with self.lock:
            self.data_bank.set_coils(address, values)

    def get_discrete_inputs(self, address, count):
        with self.lock:
            return self.data_bank.get_discrete_inputs(address, count)

    def set_discrete_inputs(self, address, values):
        with self.lock:
            self.data_bank.set_discrete_inputs(address, values)

    def get_input_registers(self, address, count):
        with self.lock:
            return self.data_bank.get_input_registers(address, count)

    def set_input_registers(self, address, values):
        with self.lock:
            self.data_bank.set_input_registers(address, values)

    def get_holding_registers(self, address, count):
        with self.lock:
            return self.data_bank.get_holding_registers(address, count)

    def set_holding_registers(self, address, values):
        with self.lock:
            self.data_bank.set_holding_registers(address, values)

    def increment_holding_register(self, address):
        with self.lock:
            current = self.data_bank.get_holding_registers(address, 1)[0]
            self.data_bank.set_holding_registers(address, [current + 1])
            return current + 1

    def toggle_coil(self, address):
        with self.lock:
            current = self.data_bank.get_coils(address, 1)[0]
            new_val = not current
            self.data_bank.set_coils(address, [new_val])
            return new_val

    def bind_to_server(server):
        """
        Attaches a SafeDataBank wrapper to a Modbus server.
        Usage: server.safe_bank = SafeDataBank.bind_to_server(server)
        """
        wrapper = SafeDataBank(server.data_bank)
        server.safe_bank = wrapper
        return wrapper

    def reset_all(self, coil_count=8, register_count=8):
        with self.lock:
            self.data_bank.set_coils(0, [False] * coil_count)
            self.data_bank.set_holding_registers(0, [0] * register_count)
            self.data_bank.set_input_registers(0, [0] * register_count)
            self.data_bank.set_discrete_inputs(0, [False] * coil_count)
