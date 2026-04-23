from dataclasses import dataclass


@dataclass
class FakeGPSHandle:
    sample_count: int = 0


def init_gps():
    return FakeGPSHandle()


def try_read_gps(gps_handle: FakeGPSHandle):
    """
    Predictable GPS pattern:
      lat = 53.000000 + 0.001 * n
      lon = -113.000000 - 0.001 * n
      alt = 700.0 + n
      fix_ok = True always
      utc_time_str = "120000", "120001", "120002", ...

    If you want to simulate "no new fix", uncomment the None block below.
    """
    n = gps_handle.sample_count
    gps_handle.sample_count += 1

    # Optional: simulate missing fix every 5th read
    # if n > 0 and n % 5 == 0:
    #     return None

    lat = 53.000000 + (0.001 * n)
    lon = -113.000000 - (0.001 * n)
    alt_m = 700.0 + n
    fix_ok = True
    utc_time_str = f"1200{n:02d}"

    return lat, lon, alt_m, fix_ok, utc_time_str