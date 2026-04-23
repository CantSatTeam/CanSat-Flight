import threading
import time

import drivers_test.camera as camera
from config import *

def camera_task(stop_event, state):
    handle = camera.init_camera()

    try:
        while not stop_event.is_set():
            try:
                path = camera.take_photo(handle)
                if path is not None:
                    state.set_image_path(path)
                else:
                    state.set_health_flag("camera_ok", False)
            except Exception as e:
                state.set_health_flag("camera_ok", False)
                print(f"[CAMERA ERROR] {e}")

            stop_event.wait(CAMERA_INTERVAL)
    finally:
        camera.close_camera(handle)