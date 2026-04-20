from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import pynmea2
import serial


@dataclass
class GPSFix:
    lat: float
    lon: float
    alt_msl_m: float | None
    geoid_sep_m: float | None
    ellipsoid_alt_m: float | None
    fix_quality: int
    num_sats: int | None
    hdop: float | None
    utc_datetime: str | None
    source_talker: str
    raw_gga: str
    raw_rmc: str | None


def _to_float(x):
    try:
        return float(x)
    except Exception:
        return None


def _to_int(x):
    try:
        return int(x)
    except Exception:
        return None


def parse_nmea_lines(lines: Iterable[str], max_wait_s: float | None = None) -> GPSFix | None:
    latest_rmc_iso = None
    latest_rmc_raw = None
    start = time.time()

    for line in lines:
        if max_wait_s is not None and (time.time() - start) > max_wait_s:
            break

        line = line.strip()
        if not line or not line.startswith("$"):
            continue

        try:
            msg = pynmea2.parse(line)
        except pynmea2.ParseError:
            continue

        sentence_type = getattr(msg, "sentence_type", "")
        talker = getattr(msg, "talker", "")

        if sentence_type == "RMC":
            status = getattr(msg, "status", "")
            datestamp = getattr(msg, "datestamp", None)
            timestamp = getattr(msg, "timestamp", None)
            if status == "A" and datestamp and timestamp:
                dt = datetime.combine(datestamp, timestamp).replace(tzinfo=timezone.utc)
                latest_rmc_iso = dt.isoformat()
                latest_rmc_raw = line

        elif sentence_type == "GGA":
            fix_quality = _to_int(getattr(msg, "gps_qual", None)) or 0
            lat = _to_float(getattr(msg, "latitude", None))
            lon = _to_float(getattr(msg, "longitude", None))
            if fix_quality <= 0 or lat is None or lon is None:
                continue

            alt_msl = _to_float(getattr(msg, "altitude", None))
            geoid_sep = _to_float(getattr(msg, "geo_sep", None))
            ellipsoid_alt = None
            if alt_msl is not None and geoid_sep is not None:
                ellipsoid_alt = alt_msl + geoid_sep

            return GPSFix(
                lat=lat,
                lon=lon,
                alt_msl_m=alt_msl,
                geoid_sep_m=geoid_sep,
                ellipsoid_alt_m=ellipsoid_alt,
                fix_quality=fix_quality,
                num_sats=_to_int(getattr(msg, "num_sats", None)),
                hdop=_to_float(getattr(msg, "horizontal_dil", None)),
                utc_datetime=latest_rmc_iso,
                source_talker=talker,
                raw_gga=line,
                raw_rmc=latest_rmc_raw,
            )

    return None


def serial_line_source(port: str = "/dev/serial0", baud: int = 9600, timeout: float = 1.0):
    ser = serial.Serial(port, baudrate=baud, timeout=timeout)
    try:
        while True:
            raw = ser.readline()
            if not raw:
                continue
            yield raw.decode("ascii", errors="replace")
    finally:
        ser.close()


def file_line_source(path: str):
    with open(path, "r", encoding="ascii", errors="replace") as f:
        for line in f:
            yield line


def get_gps_fix(
    *,
    lat: float | None = None,
    lon: float | None = None,
    alt_m: float | None = None,
    gps_nmea_file: str | None = None,
    gps_port: str = "/dev/serial0",
    gps_baud: int = 9600,
    gps_timeout: float = 1.0,
    gps_max_wait_s: float = 20.0,
    min_fix_quality: int | None = 1,
    min_sats: int | None = 4,
    max_hdop: float | None = 5.0,
) -> GPSFix:
    if lat is not None and lon is not None:
        return GPSFix(
            lat=float(lat),
            lon=float(lon),
            alt_msl_m=float(alt_m) if alt_m is not None else None,
            geoid_sep_m=None,
            ellipsoid_alt_m=None,
            fix_quality=1,
            num_sats=None,
            hdop=None,
            utc_datetime=datetime.now(timezone.utc).isoformat(),
            source_talker="MANUAL",
            raw_gga="",
            raw_rmc=None,
        )

    if gps_nmea_file:
        fix = parse_nmea_lines(file_line_source(gps_nmea_file), max_wait_s=None)
    else:
        fix = parse_nmea_lines(
            serial_line_source(gps_port, gps_baud, gps_timeout),
            max_wait_s=gps_max_wait_s,
        )

    if fix is None:
        raise RuntimeError("No valid GPS fix found")

    if min_fix_quality is not None and fix.fix_quality < min_fix_quality:
        raise RuntimeError(f"GPS fix quality {fix.fix_quality} below minimum {min_fix_quality}")

    if max_hdop is not None and fix.hdop is not None and fix.hdop > max_hdop:
        raise RuntimeError(f"GPS HDOP {fix.hdop} worse than allowed maximum {max_hdop}")

    if min_sats is not None and fix.num_sats is not None and fix.num_sats < min_sats:
        raise RuntimeError(f"GPS satellites {fix.num_sats} below minimum {min_sats}")

    return fix