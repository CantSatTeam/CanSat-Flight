from __future__ import annotations

from dataclasses import dataclass
import time

from data.packets import GPSFrame


@dataclass
class FakeGPSHandle:
    sample_count: int = 0


def init_gps() -> FakeGPSHandle:
    return FakeGPSHandle()


def close_gps(handle: FakeGPSHandle) -> None:
    # Fake GPS has nothing to close.
    pass


def try_read_gps(handle: FakeGPSHandle) -> GPSFrame | None:
    """
    Predictable GPS pattern:
      lat = 53.000000 + 0.001 * n
      lon = -113.000000 - 0.001 * n
      alt = 700.0 + n
      fix_ok = True always
      utc_time_str = "120000", "120001", "120002", ...
    """
    n = handle.sample_count
    handle.sample_count += 1

    # Optional: simulate missing fix every 5th read
    # if n > 0 and n % 5 == 0:
    #     return None

    return GPSFrame(
        monotonic_s=time.monotonic(),
        lat_deg=53.000000 + (0.001 * n),
        lon_deg=-113.000000 - (0.001 * n),
        alt_m=700.0 + n,
        fix_ok=True,
        utc_time_str=f"1200{n:02d}",
    )