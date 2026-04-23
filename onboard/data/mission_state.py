from data.packets import *
import time
import threading
from typing import Optional

# Thread safe shared state for latest sensor readings and health status.
# This is a simple implementation using a lock
# could be optimized with more advanced concurrency stuff
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.latest_bme: Optional[BMEFrame] = None
        self.latest_gps: Optional[GPSFrame] = None
        self.health = {
            "bme_ok": False,
            "gps_ok": False,
            "radio_ok": False,
            "last_bme_s": 0.0,
            "last_gps_s": 0.0,
            "last_telem_s": 0.0,
            "last_radio_s": 0.0,
        }

    def set_bme(self, frame: BMEFrame):
        with self.lock:
            self.latest_bme = frame
            self.health["bme_ok"] = True
            self.health["last_bme_s"] = time.monotonic()

    def set_gps(self, frame: GPSFrame):
        with self.lock:
            self.latest_gps = frame
            self.health["gps_ok"] = True
            self.health["last_gps_s"] = time.monotonic()

    def set_health_flag(self, key: str, value):
        with self.lock:
            self.health[key] = value

    def snapshot(self):
        with self.lock:
            return self.latest_bme, self.latest_gps, dict(self.health)
