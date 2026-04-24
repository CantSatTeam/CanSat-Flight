from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import time

from PIL import Image

from config import CAMERA_DIR


@dataclass
class CameraHandle:
    image_dir: Path


def init_camera() -> CameraHandle:
    image_dir = Path(CAMERA_DIR)

    if not image_dir.is_absolute():
        image_dir = Path.cwd() / image_dir

    image_dir.mkdir(parents=True, exist_ok=True)
    return CameraHandle(image_dir=image_dir)


def close_camera(handle: CameraHandle) -> None:
    pass


def take_photo(handle: CameraHandle, filename: Optional[str] = None) -> Optional[str]:
    if filename is None:
        filename = f"image_{int(time.time())}.jpg"

    path = handle.image_dir / filename

    try:
        image = Image.new("RGB", (640, 480), color=(0, 0, 0))
        image.save(path, format="JPEG")
        return str(path)
    except Exception:
        return None