from pyModbusTCP.server import ModbusServer
import threading
import time
import sys
import termios
import tty

# Get a single character from the terminal (blocking)
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Thread to toggle coils on keypress
def listen_for_keys(server: ModbusServer):
    print("Press number keys 0–7 to toggle coils. Ctrl+C to exit.")
    while True:
        ch = getch()
        if ch and ch.isdigit():
            idx = int(ch)
            if 0 <= idx <= 7:
                current = server.data_bank.get_coils(idx, 1)
                if current:
                    new_val = not current[0]
                    server.data_bank.set_coils(idx, [new_val])
                    print(f"Toggled coil {idx} to {'ON' if new_val else 'OFF'}")
        time.sleep(0.05)

# Thread to print all coil states
def print_coil_states(server: ModbusServer):
    while True:
        states = server.data_bank.get_coils(0, 8)
        status = " | ".join([f"{i}:{'ON' if s else 'OFF'}" for i, s in enumerate(states)])
        print("Server Coil States:", status)
        time.sleep(1)

# Main entry point
if __name__ == "__main__":
    server = ModbusServer(host="0.0.0.0", port=502, no_block=True)

    try:
        print("Starting Modbus server...")
        server.start()
        server.data_bank.set_coils(0, [False] * 8)

        threading.Thread(target=listen_for_keys, args=(server,), daemon=True).start()
        threading.Thread(target=print_coil_states, args=(server,), daemon=True).start()

        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping server.")
        server.stop()

