import time
import threading
from data.mission_state import SharedState

def watchdog_task(stop_event: threading.Event, state: SharedState):
    """
    health monitor
    will actually implement later this is just a placeholder to make sure the thread is running and can access state.
    Later, have states like BOOT, SELF_TEST, FLIGHT,etc

    """
    while not stop_event.is_set():
        _, _, health = state.snapshot()
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

        stop_event.wait(1.0)