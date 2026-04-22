from config import *
import bme280
import smbus2

_bme_bus = None
_bme_cal_loaded = False

def init_bme():
    global _bme_bus, _bme_cal_loaded
    _bme_bus = smbus2.SMBus(BME_PORT)
    bme280.load_calibration_params(_bme_bus, BME_ADDRESS)
    _bme_cal_loaded = True

def read_bme():
    if _bme_bus is None or not _bme_cal_loaded:
        raise RuntimeError("BME280 not initialized")
    sample = bme280.sample(_bme_bus, BME_ADDRESS)
    return sample.temperature, sample.pressure, sample.humidity