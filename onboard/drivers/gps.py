# =========================
# Drivers: GPS
# Replace with real UART + pynmea2 parser
# =========================

def init_gps():
    # Example:
    # import serial
    # ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=0.2)
    # return ser
    return object()

def try_read_gps(gps_handle):
    """
    Return either:
      (lat, lon, alt_m, fix_ok, utc_time_str)
    or:
      None if no new valid fix is available
    """
    # Placeholder: no fix
    return None