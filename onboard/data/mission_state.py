from data.packets import *
import time
import threading
from typing import Optional


class SharedState:
    def __init__(self):
        self.lock = threading.Lock()

        self.latest_bme: Optional[BMEFrame] = None
        self.latest_gps: Optional[GPSFrame] = None
        self.last_image_path: Optional[str] = None

        self.health = {
            "bme_ok": False,
            "gps_ok": False,
            "radio_ok": False,
            "camera_ok": False,
            "last_bme_s": 0.0,
            "last_gps_s": 0.0,
            "last_telem_s": 0.0,
            "last_radio_s": 0.0,
            "last_camera_s": 0.0,
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

    def set_image_path(self, path: str):
        with self.lock:
            self.last_image_path = path
            self.health["camera_ok"] = True
            self.health["last_camera_s"] = time.monotonic()

    def set_health_flag(self, key: str, value):
        with self.lock:
            self.health[key] = value

    def snapshot(self):
        with self.lock:
            return (
                self.latest_bme,
                self.latest_gps,
                self.last_image_path,
                dict(self.health),
            )