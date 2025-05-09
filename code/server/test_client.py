from pyModbusTCP.client import ModbusClient

MODBUS_HOST = "192.168.1.10"
MODBUS_PORT = 502

def main():
    client = ModbusClient(host=MODBUS_HOST, port=MODBUS_PORT, auto_open=True)

    coil = client.write_single_coil(2, True)
    if coil:
        print("Write succesfull")
    else:
        print("Write failed")
    # while True:
    #     if client.open():
    #         coil = client.read_coils(4, 1)
    #         if coil:
    #             print(f"Coil 1 value: {coil[0]}")
    #         else:
    #             print("Failed to read coil 0.")
    #         client.close()
    #     else:
    #         print("Unable to connect to Modbus server at 192.168.1.10:502.")

if __name__ == "__main__":
    main()
