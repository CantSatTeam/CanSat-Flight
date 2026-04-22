import queue
import threading
from config import *
import os

def ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def append_log_line(line: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def logger_task(stop_event: threading.Event, log_queue: queue.Queue):
    ensure_log_dir()

    while not stop_event.is_set():
        try:
            line = log_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        try:
            append_log_line(line)
        except Exception as e:
            print(f"[LOG ERROR] {e}")