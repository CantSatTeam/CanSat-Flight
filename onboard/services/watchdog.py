import time
import threading
from data.mission_state import SharedState


def watchdog_task(stop_event: threading.Event, state: SharedState):
    while not stop_event.is_set():
        _, _, _, _, _, health = state.snapshot()
        now = time.monotonic()

        if health["last_bme_s"] and (now - health["last_bme_s"] > 3.0):
            print("[SUPERVISOR] BME stale")
            state.set_health_flag("bme_ok", False)

        if health["last_gps_s"] and (now - health["last_gps_s"] > 10.0):
            print("[SUPERVISOR] GPS stale")
            state.set_health_flag("gps_ok", False)

        if health["last_radio_s"] and (now - health["last_radio_s"] > 5.0):
            print("[SUPERVISOR] Radio stale")
            state.set_health_flag("radio_ok", False)
            
        # if health["inference_running"] and health["last_inference_s"]:
        #     # optional: only warn if you expect a cadence
        #     pass

        stop_event.wait(1.0)