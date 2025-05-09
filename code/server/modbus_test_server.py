from pyModbusTCP.server import ModbusServer
import threading
import time
import sys
import termios
import tty
import os

# Define key-to-register mappings (input registers)
INPUT_REGISTER_KEYS = {
    '1': 0,  # Register 0
    '2': 1,  # Register 1
}

# Coil mapping (e.g., start button)
COIL_KEYS = {
    '0': 0  # Coil 0 toggled by key '0'
}

# Get a single character from the terminal (blocking)
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Thread to handle keypresses
def listen_for_keys(server: ModbusServer):
    print("Press keys to interact with Modbus server. Ctrl+C to exit.")
    while True:
        ch = getch()
        if ch in COIL_KEYS:
            idx = COIL_KEYS[ch]
            current = server.data_bank.get_coils(idx, 1)[0]
            server.data_bank.set_coils(idx, [not current])
            print(f"Toggled coil {idx} to {'ON' if not current else 'OFF'}")

        elif ch in INPUT_REGISTER_KEYS:
            reg = INPUT_REGISTER_KEYS[ch]
            current = server.data_bank.get_input_registers(reg, 1)[0]
            server.data_bank.set_input_registers(reg, [current + 1])
            print(f"Incremented input register {reg} to {current + 1}")

        elif ch == 'r':
            for reg in INPUT_REGISTER_KEYS.values():
                server.data_bank.set_input_registers(reg, [0])
            for coil in COIL_KEYS.values():
                server.data_bank.set_coils(coil, [False])
            print("Reset all input registers and coils.")

        time.sleep(0.05)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Thread to print all register and coil states
def print_state(server: ModbusServer):
    while True:
        clear_screen()
        coils = server.data_bank.get_coils(0, 8)
        coil_status = " | ".join([f"C{i}:{'ON' if s else 'OFF'}" for i, s in enumerate(coils)])
        inputs = server.data_bank.get_input_registers(0, 8)
        input_status = " | ".join([f"IR{i}:{v}" for i, v in enumerate(inputs)])
        print("📟 Modbus Coil States:")
        print(coil_status)
        print("\n📊 Input Register Counts:")
        print(input_status)
        time.sleep(1)

# Main entry point
if __name__ == "__main__":
    server = ModbusServer(host="0.0.0.0", port=502, no_block=True)

    try:
        print("Starting Modbus server...")
        server.start()
        server.data_bank.set_coils(0, [False] * 8)
        server.data_bank.set_input_registers(0, [0] * 8)

        threading.Thread(target=listen_for_keys, args=(server,), daemon=True).start()
        threading.Thread(target=print_state, args=(server,), daemon=True).start()

        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping server.")
        server.stop()
