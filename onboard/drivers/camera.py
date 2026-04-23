from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import time

from picamzero import Camera

from config import CAMERA_DIR


@dataclass
class CameraHandle:
    cam: Camera
    image_dir: Path


def init_camera() -> CameraHandle:
    base = Path.home() / "CanSat-Flight"
    image_dir = Path(CAMERA_DIR)

    if not image_dir.is_absolute():
        image_dir = base / image_dir

    image_dir.mkdir(parents=True, exist_ok=True)

    return CameraHandle(
        cam=Camera(),
        image_dir=image_dir,
    )


def close_camera(handle: CameraHandle) -> None:
    close_fn = getattr(handle.cam, "close", None)
    if callable(close_fn):
        try:
            close_fn()
        except Exception:
            pass


def take_photo(handle: CameraHandle, filename: Optional[str] = None) -> Optional[str]:
    if filename is None:
        filename = f"image_{int(time.time())}.jpg"

    path = handle.image_dir / filename

    try:
        handle.cam.take_photo(str(path))
        return str(path)
    except Exception:
        return None