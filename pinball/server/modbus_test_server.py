from pyModbusTCP.server import ModbusServer
import threading
import time
import sys
import termios
import tty
import os
import json

DEVICE_PATH = "../config/devices.json"

# Load device mappings
with open(DEVICE_PATH) as f:
    config = json.load(f)["devices"]

coil_keys = {}
register_keys = {}
coil_name_map = {}
register_name_map = {}

# Auto-map keys
next_coil_key = ord('a')
next_reg_key = ord('1')

for name, props in config.items():
    addr = props["address"] - 1  # Modbus is 1-based
    if props["reg_type"] == "coil":
        key = chr(next_coil_key)
        coil_keys[key] = addr
        coil_name_map[addr] = name
        next_coil_key += 1
    elif props["reg_type"] == "input_register":
        key = chr(next_reg_key)
        register_keys[key] = addr
        register_name_map[addr] = name
        next_reg_key += 1

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def listen_for_keys(server: ModbusServer):
    print("Press keys to toggle coils or increment registers. 'r' = reset. Ctrl+C to exit.\n")
    print("Mapped keys:")
    for k, a in coil_keys.items():
        print(f"  {k} → toggle coil '{coil_name_map[a]}' (address {a+1})")
    for k, a in register_keys.items():
        print(f"  {k} → increment register '{register_name_map[a]}' (address {a+1})")
    print()
    
    while True:
        ch = getch()
        if ch in coil_keys:
            idx = coil_keys[ch]
            current = server.data_bank.get_coils(idx, 1)[0]
            server.data_bank.set_coils(idx, [not current])
            print(f"Toggled coil {idx+1} ({coil_name_map[idx]}) → {'ON' if not current else 'OFF'}")

        elif ch in register_keys:
            reg = register_keys[ch]
            current = server.data_bank.get_input_registers(reg, 1)[0]
            server.data_bank.set_input_registers(reg, [current + 1])
            print(f"Incremented input register {reg+1} ({register_name_map[reg]}) → {current + 1}")

        elif ch == 'r':
            for addr in coil_name_map:
                server.data_bank.set_coils(addr, [False])
            for addr in register_name_map:
                server.data_bank.set_input_registers(addr, [0])
            print("✅ All coils and input registers reset.")
        time.sleep(0.05)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_state(server: ModbusServer):
    while True:
        clear_screen()
        print("📟 Coils:")
        for addr in sorted(coil_name_map):
            val = server.data_bank.get_coils(addr, 1)[0]
            key = next((k for k, a in coil_keys.items() if a == addr), "?")
            print(f"[{key}] {coil_name_map[addr]:<30} (addr {addr+1}): {'ON' if val else 'OFF'}")

        print("\n📊 Input Registers:")
        for addr in sorted(register_name_map):
            val = server.data_bank.get_input_registers(addr, 1)[0]
            key = next((k for k, a in register_keys.items() if a == addr), "?")
            print(f"[{key}] {register_name_map[addr]:<30} (addr {addr+1}): {val}")
        time.sleep(1)


if __name__ == "__main__":
    server = ModbusServer(host="0.0.0.0", port=502, no_block=True)

    try:
        print("Starting Modbus test server...")
        server.start()

        # Clear initial values
        for addr in coil_name_map:
            server.data_bank.set_coils(addr, [False])
        for addr in register_name_map:
            server.data_bank.set_input_registers(addr, [0])

        threading.Thread(target=listen_for_keys, args=(server,), daemon=True).start()
        threading.Thread(target=print_state, args=(server,), daemon=True).start()

        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping server.")
        server.stop()
