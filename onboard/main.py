import time
import board

### SHT4x Initialization ###

import adafruit_sht4x

i2c = board.I2C()   # uses board.SCL and board.SDA
sht = adafruit_sht4x.SHT4x(i2c)
print("Found SHT4x with serial number", hex(sht.serial_number))

sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])

### E22 Initialization ###

from lora_e22 import LoRaE22
import busio

# Create a UART object to communicate with the LoRa module with ESP32
uart2 = busio.UART(board.TX, board.RX, baudrate=9600)
# Create a LoRaE22 object, passing the UART object and pin configurations
lora = LoRaE22('400T22D', uart2, aux_pin=board.D15, m0_pin=board.D21, m1_pin=board.D19)

### E22 "Start Transmission" ###

code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

### Main Loop ###

while True:
    # Read SHT4x
    temperature, relative_humidity = sht.measurements
    print("Temperature: %0.1f C" % temperature)
    print("Humidity: %0.1f %%" % relative_humidity)
    print("")

    # Compile data string
    data=f"{temperature*10:.0f},{relative_humidity*10:.0f}"
    print("Data string:", data)

    # Transmit via E22
    lora.send_transparent_message(data)

    # 1 Hz
    time.sleep(1)
