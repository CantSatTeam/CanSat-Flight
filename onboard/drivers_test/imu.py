_sample_index = 0
_started = False


def init_imu():
    global _started, _sample_index
    _started = True
    _sample_index = 0


def read_imu():
    """
    Predictable IMU pattern:
      accel_x = 0, 1, 2, 3, ...
      accel_y = 10, 11, 12, ...
      accel_z = 20, 21, 22, ...

      gyro_x = 30, 31, 32, ...
      gyro_y = 40, 41, 42, ...
      gyro_z = 50, 51, 52, ...

      mag_x = 60, 61, 62, ...
      mag_y = 70, 71, 72, ...
      mag_z = 80, 81, 82, ...
    """
    global _sample_index

    if not _started:
        raise RuntimeError("Fake IMU not initialized")

    i = _sample_index
    _sample_index += 1

    return {
        "accel_x_mps2": float(i),
        "accel_y_mps2": float(10 + i),
        "accel_z_mps2": float(20 + i),
        "gyro_x_dps": float(30 + i),
        "gyro_y_dps": float(40 + i),
        "gyro_z_dps": float(50 + i),
        "mag_x_ut": float(60 + i),
        "mag_y_ut": float(70 + i),
        "mag_z_ut": float(80 + i),
    }