from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np

from gps_reader import get_gps_fix
from geo_crop import localize_and_crop


LOG = logging.getLogger("main")


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _safe_json_default(obj):
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def build_argparser():
    p = argparse.ArgumentParser(
        description="GPS + ORB localization against orthophoto, then crop DSM"
    )

    p.add_argument("--ortho", required=True, help="Georeferenced orthophoto GeoTIFF")
    p.add_argument("--dsm", required=True, help="Georeferenced DSM GeoTIFF")
    p.add_argument("--camera", required=True, help="Camera frame image path")

    p.add_argument("--out-dsm", default="cropped_dsm.tif", help="Output DSM crop")
    p.add_argument("--out-meta", default="cropped_dsm_metadata.json", help="Output metadata JSON")

    p.add_argument("--lat", type=float, default=None)
    p.add_argument("--lon", type=float, default=None)
    p.add_argument("--alt-m", type=float, default=None)

    p.add_argument("--gps-nmea-file", default=None)
    p.add_argument("--gps-port", default="/dev/serial0")
    p.add_argument("--gps-baud", type=int, default=9600)
    p.add_argument("--gps-timeout", type=float, default=1.0)
    p.add_argument("--gps-max-wait-s", type=float, default=20.0)

    p.add_argument("--min-fix-quality", type=int, default=1)
    p.add_argument("--min-sats", type=int, default=4)
    p.add_argument("--max-hdop", type=float, default=5.0)

    p.add_argument("--coarse-search-m", type=float, default=120.0)
    p.add_argument("--final-crop-m", type=float, default=40.0)

    p.add_argument("--orb-ratio-thresh", type=float, default=0.75)
    p.add_argument("--orb-min-good", type=int, default=40)
    p.add_argument("--orb-min-inliers", type=int, default=20)
    p.add_argument("--camera-max-dim", type=int, default=960)
    p.add_argument("--mapchip-max-dim", type=int, default=1400)
    p.add_argument("--max-refinement-shift-m", type=float, default=60.0)
    p.add_argument("--require-orb", action="store_true")

    p.add_argument("--verbose", action="store_true")
    return p


def main():
    args = build_argparser().parse_args()
    setup_logging(args.verbose)

    try:
        fix = get_gps_fix(
            lat=args.lat,
            lon=args.lon,
            alt_m=args.alt_m,
            gps_nmea_file=args.gps_nmea_file,
            gps_port=args.gps_port,
            gps_baud=args.gps_baud,
            gps_timeout=args.gps_timeout,
            gps_max_wait_s=args.gps_max_wait_s,
            min_fix_quality=args.min_fix_quality,
            min_sats=args.min_sats,
            max_hdop=args.max_hdop,
        )

        LOG.info(
            "GPS fix lat=%.8f lon=%.8f fixq=%s sats=%s hdop=%s",
            fix.lat, fix.lon, fix.fix_quality, fix.num_sats, fix.hdop
        )

        result = localize_and_crop(
            ortho_path=args.ortho,
            dsm_path=args.dsm,
            camera_path=args.camera,
            gps_lat=fix.lat,
            gps_lon=fix.lon,
            coarse_search_m=args.coarse_search_m,
            final_crop_m=args.final_crop_m,
            orb_ratio_thresh=args.orb_ratio_thresh,
            orb_min_good=args.orb_min_good,
            orb_min_inliers=args.orb_min_inliers,
            camera_max_dim=args.camera_max_dim,
            mapchip_max_dim=args.mapchip_max_dim,
            max_refinement_shift_m=args.max_refinement_shift_m,
            require_orb=args.require_orb,
            out_dsm=args.out_dsm,
        )

        payload = {
            "status": "ok",
            "gps_fix": asdict(fix),
            "result": result,
            "params": vars(args),
        }

        Path(args.out_meta).write_text(
            json.dumps(payload, indent=2, default=_safe_json_default),
            encoding="utf-8",
        )

        print(json.dumps(payload, indent=2, default=_safe_json_default))

    except Exception as e:
        LOG.exception("Pipeline failed")
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()