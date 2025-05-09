
import json
import threading
import time
from typing import Dict
from pyModbusTCP.client import ModbusClient
from core.device import Device

class ModbusClientAPI:
    def __init__(self, host: str, port: int, config_path: str, poll_interval: float = 0.1):
        self.host = host
        self.port = port
        self.poll_interval = poll_interval
        self.lock = threading.Lock()
        self.client = ModbusClient(host=host, port=port, auto_open=True)
        self.devices: Dict[str, Device] = {}
        self.inputs: Dict[str, int] = {}
        self.running = True

        self._load_config(config_path)
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def _load_config(self, path: str):
        with open(path, 'r') as f:
            config = json.load(f)

        for name, props in config.get("devices", {}).items():
            score = props.get("score", 0)
            device = Device(
                name=name,
                address=props["address"],
                reg_type=props["reg_type"],
                direction=props["direction"],
                score=score
            )
            self.devices[name] = device

    def _poll_loop(self):
        while self.running:
            with self.lock:
                for device in self.devices.values():
                    if device.reg_type == "coil":
                        result = self.client.read_coils(device.address-1, 1)
                    elif device.reg_type == "input_register":
                        result = self.client.read_input_registers(device.address-1, 1)
                    elif device.reg_type == "holding_register":
                        result = self.client.read_holding_registers(device.address-1, 1)
                    else:
                        result = None
                    
                    if result:
                        self.inputs[device.name] = int(result[0])
                    else:
                        self.inputs[device.name] = 0
            time.sleep(self.poll_interval)

    def read_value(self, name: str) -> int:
        with self.lock:
            return self.inputs.get(name, 0)

    def read_all(self) -> Dict[str, int]:
        with self.lock:
            return dict(self.inputs)
    
    def write_value(self, name: str, value: int):
        """
        Set a coil value (0 or 1) by device name.
        Only works on devices defined as coils with direction 'output'.
        """
        with self.lock:
            device = self.devices.get(name)
            if not device:
                print(f"[ModbusClientAPI] Device '{name}' not found.")
                return False
            if device.reg_type != "coil" or device.direction != "output":
                print(f"[ModbusClientAPI] Device '{name}' is not a writable coil.")
                return False

            success = self.client.write_single_coil(device.address-1, value)
            if success:
                print(f"[ModbusClientAPI] Coil '{name}' set to {value} at address {device.address}")
            else:
                print(f"[ModbusClientAPI] Failed to write to coil '{name}' at address {device.address}")
            return success

    def stop(self):
        self.running = False
        self.thread.join()
        self.client.close()

if __name__ == "__main__":
    ip_addr = "192.168.1.10"
    # ip_addr = "localhost"
    api = ModbusClientAPI(ip_addr, 502, "../config/devices.json")
    try:
        count = 1
        while True:
            print(f"--- Read {count} ---")
            inputs = api.read_all()
            for name, val in sorted(inputs.items()):
                state = "ON  " if val else "OFF "
                print(f"{name:<15}: {state}")
            print()
            time.sleep(0.5)
            count += 1
    except KeyboardInterrupt:
        print("\nStopping Modbus client.")
    finally:
        api.stop()

