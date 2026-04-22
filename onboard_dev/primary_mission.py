import time

### Logging ###

import os

log_path = "onboard/logs/primary_log.txt"

def log(line):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())

### BME280 ###

import bme280
import smbus2

bme_port = 1
bme_address = 0x76 # Adafruit BME280 is 0x77, but we have 0x76
bme_bus = None

def init_bme():
    global bme_port, bme_address, bme_bus
    bme_bus = smbus2.SMBus(bme_port)
    bme280.load_calibration_params(bme_bus,bme_address)

def query_bme():
    global bme_port, bme_address, bme_bus
    bme280_data = bme280.sample(bme_bus,bme_address)
    return bme280_data

### LoRa E22 ###

def init_lora():
    pass

def transmit_lora_transparent(string: str):
    pass

### Main Loop ###

init_bme()
init_lora()

while True:
    # Read BME280
    bme280_data = query_bme()
    humidity = bme280_data.humidity
    pressure = bme280_data.pressure
    ambient_temperature = bme280_data.temperature

    # Debug
    print("Temperature: %0.1f C" % ambient_temperature)
    print("Pressure: %0.1f hPa" % pressure)
    print("Humidity: %0.1f %%" % humidity)
    print("")

    # Compile data string
    data = f"{ambient_temperature*10:.0f},{pressure*10:.0f}"

    # Log and transmit
    print("Data string: ", data)
    transmit_lora_transparent(data)
    log(data)

    # 1 Hz
    time.sleep(1)
