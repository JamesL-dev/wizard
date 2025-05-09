
import json
import threading
import time
from typing import Dict
from pyModbusTCP.client import ModbusClient

class Device:
    def __init__(self, name: str, address: int, reg_type: str, direction: str):
        self.name = name
        self.address = address
        self.reg_type = reg_type
        self.direction = direction

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
            if props.get("direction") == "input":
                device = Device(
                    name=name,
                    address=props["address"],
                    reg_type=props["reg_type"],
                    direction=props["direction"]
                )
                self.devices[name] = device

    def _poll_loop(self):
        while self.running:
            with self.lock:
                for device in self.devices.values():
                    if device.reg_type == "coil":
                        result = self.client.read_coils(device.address, 1)
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

    def stop(self):
        self.running = False
        self.thread.join()
        self.client.close()

if __name__ == "__main__":
    api = ModbusClientAPI("localhost", 502, "devices.json")
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

