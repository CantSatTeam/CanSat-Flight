def init_bme():
    global _started, _sample_index
    _started = True
    _sample_index = 0


def read_bme():
    """
    Very simple predictable pattern:
      temp     = 20.0, 21.0, 22.0, ...
      pressure = 1000.0, 1001.0, 1002.0, ...
      humidity = 40.0, 41.0, 42.0, ...
    """
    global _sample_index

    if not _started:
        raise RuntimeError("Fake BME280 not initialized")

    i = _sample_index
    _sample_index += 1

    temperature_c = 20.0 + i
    pressure_hpa = 1000.0 + i
    humidity_pct = 40.0 + i

    return temperature_c, pressure_hpa, humidity_pct