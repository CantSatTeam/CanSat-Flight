from dataclasses import dataclass
from typing import Optional

@dataclass
class BMEFrame:
    monotonic_s: float
    ambient_temp_c: float
    pressure_hpa: float
    humidity_pct: float

@dataclass
class GPSFrame:
    monotonic_s: float
    lat_deg: float
    lon_deg: float
    alt_m: float
    fix_ok: bool
    utc_time_str: str

@dataclass
class TelemetryFrame:
    seq: int
    monotonic_s: float
    ambient_temp_c: float
    pressure_hpa: float
    humidity_pct: float
    gps_valid: int
    lat_deg: Optional[float]
    lon_deg: Optional[float]
    alt_m: Optional[float]
    gps_time_utc: str
    bme_ok: int
    gps_ok: int
    radio_ok: int