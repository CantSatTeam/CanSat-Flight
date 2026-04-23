import queue
import threading
import time

from config import QUEUE_SIZE
import drivers_test.bme280 as bme280
from data.mission_state import SharedState
from services.camera import camera_task
from services.sampler import bme_task, gps_task
from services.telemetry import telemetry_task, radio_task
from services.logger import logger_task
from services.watchdog import watchdog_task
from services.inference import inference_task


def main():
    bme280.init_bme()

    state = SharedState()
    stop_event = threading.Event()

    radio_queue = queue.Queue(maxsize=QUEUE_SIZE)
    log_queue = queue.Queue(maxsize=QUEUE_SIZE)

    threads = [
        threading.Thread(target=bme_task, args=(stop_event, state), daemon=True),
        threading.Thread(target=gps_task, args=(stop_event, state), daemon=True),
        threading.Thread(target=telemetry_task, args=(stop_event, state, radio_queue, log_queue), daemon=True),
        threading.Thread(target=radio_task, args=(stop_event, state, radio_queue), daemon=True),
        threading.Thread(target=logger_task, args=(stop_event, log_queue), daemon=True),
        threading.Thread(target=watchdog_task, args=(stop_event, state), daemon=True),
        threading.Thread(target=camera_task, args=(stop_event, state), daemon=True),
        threading.Thread(target=inference_task, args=(stop_event, state), daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        stop_event.set()
        for t in threads:
            t.join(timeout=1.0)


if __name__ == "__main__":
    main()