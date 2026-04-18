from lora_e22 import LoRaE22
import busio
import board

# Create a UART object to communicate with the LoRa module with ESP32
uart2 = busio.UART(board.TX, board.RX, baudrate=9600)
# Create a LoRaE22 object, passing the UART object and pin configurations
lora = LoRaE22('400T22D', uart2, aux_pin=board.D15, m0_pin=board.D21, m1_pin=board.D19)

while True:
    if lora.available() > 0:
        code, value = lora.receive_message()
        print(ResponseStatusCode.get_description(code))

        print(value)
        utime.sleep_ms(2000)
