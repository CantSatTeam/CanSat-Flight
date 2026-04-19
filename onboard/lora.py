### Lora (E22 900t30s) Sensor Code
# no reference for this one
# this might be circuitpython code watch out

from lora_e22 import LoRaE22
import busio

### Pins ###

# not wired in yet

### Lora Initialization ###

# Create a UART object to communicate with the LoRa module with ESP32
uart2 = busio.UART(board.TX, board.RX, baudrate=9600)
# Create a LoRaE22 object, passing the UART object and pin configurations
lora = LoRaE22('400T22D', uart2, aux_pin=board.D15, m0_pin=board.D21, m1_pin=board.D19)

### Lora "Start Transmission" ###

code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

while True:
    # Compile data string
    data=f"6767"

    # Transmit via E22
    lora.send_transparent_message(data)

    # 1 Hz
    time.sleep(1)