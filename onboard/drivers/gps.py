from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import time

from data.packets import GPSFrame

import serial
import pynmea2

from config import *

@dataclass
class GPSHandle:
    ser: serial.Serial


def init_gps() -> GPSHandle:
    return GPSHandle(
        ser=serial.Serial(
            GPS_UART_PORT,
            GPS_BAUDRATE,
            timeout=GPS_TIMEOUT_S,
        )
    )


def close_gps(handle: GPSHandle) -> None:
    try:
        handle.ser.close()
    except Exception:
        pass


def try_read_gps(handle: GPSHandle) -> GPSFrame | None:
    try:
        line = handle.ser.readline().decode("ascii", errors="ignore").strip()
    except serial.SerialException:
        return None

    if not line.startswith("$G"):
        return None

    try:
        msg = pynmea2.parse(line)
    except pynmea2.ParseError:
        return None

    if isinstance(msg, pynmea2.types.talker.GGA):
        try:
            fix_ok = int(msg.gps_qual or 0) > 0
        except (TypeError, ValueError):
            fix_ok = False

        if not fix_ok:
            return None

        return GPSFrame(
            monotonic_s=time.monotonic(),
            lat_deg=msg.latitude,
            lon_deg=msg.longitude,
            alt_m=float(msg.altitude or 0.0),
            fix_ok=True,
            utc_time_str=msg.timestamp.isoformat() if msg.timestamp else "",
        )

    if isinstance(msg, pynmea2.types.talker.RMC):
        if getattr(msg, "status", "V") != "A":
            return None

        return GPSFrame(
            monotonic_s=time.monotonic(),
            lat_deg=msg.latitude,
            lon_deg=msg.longitude,
            alt_m=0.0,
            fix_ok=True,
            utc_time_str=msg.datetime.isoformat() if getattr(msg, "datetime", None) else "",
        )

    return None