import json
import subprocess
import time
from pathlib import Path

from config import *


def inference_task(stop_event, state):
    if not INFERENCE_ENABLED:
        print("[INFER] Disabled in config")
        state.set_health_flag("inference_ok", False)
        while not stop_event.is_set():
            stop_event.wait(1.0)
        return

    out_dir = Path(INFERENCE_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    last_key = None

    while not stop_event.is_set():
        snapshot = state.snapshot()

        # Adapt these indices/names to your actual SharedState implementation
        _bme, _gps, image_path, _unused, _unused2, _health = snapshot
        sparse_depth_path = state.get_sparse_depth_path()

        if not image_path or not sparse_depth_path:
            print("[INFER] waiting for image and sparse depth...")
            stop_event.wait(INFERENCE_POLL_S)
            continue

        job_key = (str(image_path), str(sparse_depth_path))
        if job_key == last_key:
            print("[INFER] no new data, waiting...")
            stop_event.wait(INFERENCE_POLL_S)
            continue

        state.set_health_flag("inference_running", True)

        ts = int(time.time())
        job_out_dir = out_dir / f"job_{ts}"
        job_out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            INFERENCE_PY311,
            INFERENCE_WORKER,
            "--rgb", str(image_path),
            "--sparse-depth", str(sparse_depth_path),
            "--out-dir", str(job_out_dir),
        ]

        try:
            print("[INFER] running...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=INFERENCE_TIMEOUT_S,
                check=True,
            )
            print("[INFER] done, processing output...")

            meta_path = job_out_dir / "result.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            else:
                meta = {"stdout": result.stdout[-2000:], "stderr": result.stderr[-2000:]}

            state.set_inference_result(str(job_out_dir), meta)
            state.set_health_flag("inference_ok", True)
            state.set_health_flag("last_inference_s", time.monotonic())
            print(f"[INFER] done -> {job_out_dir}")

            last_key = job_key

        except subprocess.TimeoutExpired:
            state.set_health_flag("inference_ok", False)
            print("[INFER ERROR] worker timeout")
            last_key = job_key

        except subprocess.CalledProcessError as e:
            state.set_health_flag("inference_ok", False)
            print(f"[INFER ERROR] rc={e.returncode}")
            if e.stdout:
                print(e.stdout[-2000:])
            if e.stderr:
                print(e.stderr[-2000:])
            last_key = job_key

        except Exception as e:
            state.set_health_flag("inference_ok", False)
            print(f"[INFER ERROR] {e}")
            last_key = job_key

        finally:
            state.set_health_flag("inference_running", False)

        stop_event.wait(0.1)