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
bus = None

# Retry parameters for transient I2C failures (brief brownouts)
INIT_RETRIES = 5
INIT_DELAY = 1.0

def init_bme(retries=INIT_RETRIES, delay=INIT_DELAY):
    """Open the I2C bus and load calibration params. Retry on failure."""
    global port, address, bus
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            if bus is not None:
                try:
                    bus.close()
                except Exception:
                    pass
                bus = None
            bus = smbus2.SMBus(port)
            bme280.load_calibration_params(bus, address)
            return
        except Exception as e:
            last_exc = e
            print(f"init_bme: attempt {attempt} failed: {e}")
            try:
                if bus is not None:
                    bus.close()
            except Exception:
                pass
            bus = None
            time.sleep(delay)
    raise RuntimeError(f"Failed to initialize BME280 after {retries} attempts: {last_exc}")

def run_bme():
    """Sample the sensor, reopening the bus once on I/O errors."""
    global port, address, bus
    try:
        return bme280.sample(bus, address)
    except OSError as e:
        # Try to recover once by reinitializing the bus
        print(f"run_bme: caught OSError, will retry init: {e}")
        try:
            init_bme()
            return bme280.sample(bus, address)
        except Exception as e2:
            print(f"run_bme: retry failed: {e2}")
            return None
    except Exception as e:
        print(f"run_bme: unexpected error: {e}")
        return None

### Main Loop ###

init_bme()

while True:
    bme280_data = run_bme()
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
