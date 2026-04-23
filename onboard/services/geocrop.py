import time
from pathlib import Path

from config import *
from utils.geocrop_core import localize_and_crop


def geocrop_task(stop_event, state):
    if not GEOCROP_ENABLED:
        print("[GEOCROP] Disabled in config")
        state.set_health_flag("geocrop_ok", False)
        while not stop_event.is_set():
            stop_event.wait(1.0)
        return

    out_dir = Path(GEOCROP_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    last_processed_image = None

    while not stop_event.is_set():
        _, gps, image_path, _, _, health = state.snapshot()

        if image_path is None or image_path == last_processed_image:
            stop_event.wait(0.5)
            continue

        if gps is None or not gps.fix_ok:
            print("[GEOCROP] Waiting for valid GPS before cropping")
            stop_event.wait(0.5)
            continue

        gps_age_s = time.monotonic() - health.get("last_gps_s", 0.0)
        if gps_age_s > GEOCROP_MAX_GPS_AGE_S:
            print(f"[GEOCROP] GPS too old ({gps_age_s:.1f}s); skipping {image_path}")
            state.set_health_flag("geocrop_ok", False)
            last_processed_image = image_path
            stop_event.wait(0.1)
            continue

        image_name = Path(image_path).stem
        out_path = out_dir / f"{image_name}_crop.tif"

        try:
            meta = localize_and_crop(
                ortho_path=GEOCROP_ORTHO_PATH,
                dsm_path=GEOCROP_DSM_PATH,
                camera_path=image_path,
                gps_lat=gps.lat_deg,
                gps_lon=gps.lon_deg,
                use_orb=GEOCROP_USE_ORB,
                coarse_search_m=GEOCROP_COARSE_SEARCH_M,
                final_crop_m=GEOCROP_FINAL_CROP_M,
                orb_ratio_thresh=GEOCROP_ORB_RATIO_THRESH,
                orb_min_good=GEOCROP_ORB_MIN_GOOD,
                orb_min_inliers=GEOCROP_ORB_MIN_INLIERS,
                camera_max_dim=GEOCROP_CAMERA_MAX_DIM,
                mapchip_max_dim=GEOCROP_MAPCHIP_MAX_DIM,
                orb_nfeatures=GEOCROP_ORB_NFEATURES,
                max_refinement_shift_m=GEOCROP_MAX_REFINEMENT_SHIFT_M,
                require_orb=GEOCROP_REQUIRE_ORB,
                out_dsm=str(out_path),
            )
            state.set_crop_result(str(out_path), meta)
            print(f"[GEOCROP] {meta['confidence']} -> {out_path}")
        except Exception as e:
            state.set_health_flag("geocrop_ok", False)
            print(f"[GEOCROP ERROR] {e}")

        last_processed_image = image_path
        stop_event.wait(0.1)