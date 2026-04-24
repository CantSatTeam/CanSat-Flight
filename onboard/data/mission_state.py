from data.packets import *
import time
import threading
from typing import Optional, Any


class SharedState:
    def __init__(self):
        self.lock = threading.Lock()

        self.latest_bme: Optional[BMEFrame] = None
        self.latest_gps: Optional[GPSFrame] = None
        self.last_image_path: Optional[str] = "/home/couldntsat/CanSat-MHE/terrainmesh/demo_data/RGB.png" #TEMP
        self.last_crop_path: Optional[str] = None
        self.last_crop_meta: Optional[dict[str, Any]] = None
        self.last_sparse_depth_path: Optional[str] = "/home/alexander/Projects/cansat/CanSat-Flight/pics/image_1777006184.jpg" #"/home/couldntsat/CanSat-MHE/terrainmesh/demo_data/SparseDepth.png" #TEMP
        self.last_inference_output_path: Optional[str] = None
        self.last_inference_meta: Optional[dict[str, Any]] = None

        self.health = {
            "bme_ok": False,
            "gps_ok": False,
            "radio_ok": False,
            "camera_ok": False,
            "geocrop_ok": False,
            "last_bme_s": 0.0,
            "last_gps_s": 0.0,
            "last_telem_s": 0.0,
            "last_radio_s": 0.0,
            "last_camera_s": 0.0,
            "last_geocrop_s": 0.0,
            "inference_ok": False,
            "last_inference_s": 0.0,
            "inference_running": False,
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

    def set_crop_result(self, path: str, meta: Optional[dict[str, Any]] = None):
        with self.lock:
            self.last_crop_path = path
            self.last_crop_meta = dict(meta) if meta is not None else None
            self.health["geocrop_ok"] = True
            self.health["last_geocrop_s"] = time.monotonic()

    def set_health_flag(self, key: str, value):
        with self.lock:
            self.health[key] = value
            
    def set_sparse_depth_path(self, path: str):
        with self.lock:
            self.last_sparse_depth_path = path

    def get_sparse_depth_path(self) -> Optional[str]:
        with self.lock:
            return self.last_sparse_depth_path
        
    def set_inference_result(self, path: str, meta: Optional[dict[str, Any]] = None):
        with self.lock:
            self.last_inference_output_path = path
            self.last_inference_meta = dict(meta) if meta is not None else None
            self.health["inference_ok"] = True
            self.health["last_inference_s"] = time.monotonic()

    def get_inference_result(self):
        with self.lock:
            return self.last_inference_output_path, self.last_inference_meta

    def snapshot(self):
        with self.lock:
            return (
                self.latest_bme,
                self.latest_gps,
                self.last_image_path,
                self.last_crop_path,
                self.last_crop_meta,
                dict(self.health),
            )