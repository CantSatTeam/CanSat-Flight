import time
import threading
from data.mission_state import SharedState
from data.packets import *
from config import *
import drivers.bme280 as bme280
import drivers.gps as gps


def bme_task(stop_event: threading.Event, state: SharedState):
    period = 1.0 / BME_HZ
    next_t = time.monotonic()

    while not stop_event.is_set():
        try:
            t_c, p_hpa, h_pct = bme280.read_bme()
            frame = BMEFrame(
                monotonic_s=time.monotonic(),
                ambient_temp_c=t_c,
                pressure_hpa=p_hpa,
                humidity_pct=h_pct,
            )
            state.set_bme(frame)
        except Exception as e:
            state.set_health_flag("bme_ok", False)
            print(f"[BME ERROR] {e}")

        next_t += period
        delay = max(0.0, next_t - time.monotonic())
        stop_event.wait(delay)


def gps_task(stop_event: threading.Event, state: SharedState):
    gps_handle = gps.init_gps()

    try:
        while not stop_event.is_set():
            try:
                frame = gps.try_read_gps(gps_handle)
                if frame is not None:
                    state.set_gps(frame)
            except Exception as e:
                state.set_health_flag("gps_ok", False)
                print(f"[GPS ERROR] {e}")

            stop_event.wait(0.1)
    finally:
        gps.close_gps(gps_handle)