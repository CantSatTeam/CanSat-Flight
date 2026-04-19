### BME280 Sensor Code
### https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/2

import time

import bme280
import smbus2

### Pins ###

BME_SDA = 2 # GPIO2
BME_SCL = 3 # GPIO3

### BME280 Initialization ###

port = 1
address = 0x76 # Adafruit BME280 is 0x77, but we have 0x76
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

### Main Loop ###

while True:
    bme280_data = bme280.sample(bus,address)
    humidity = bme280_data.humidity
    pressure = bme280_data.pressure
    ambient_temperature = bme280_data.temperature

    # Read BME280
    print("Temperature: %0.1f C" % ambient_temperature)
    print("Pressure: %0.1f hPa" % pressure)
    print("Humidity: %0.1f %%" % humidity)
    print("")

    # Compile data string
    data=f"{ambient_temperature*10:.0f},{pressure*10:.0f}"
    print("Data string: ", data)

    # 1 Hz
    time.sleep(1)
