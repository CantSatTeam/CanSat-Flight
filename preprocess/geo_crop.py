from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.transform import rowcol, xy
from rasterio.windows import Window
from rasterio.windows import transform as window_transform


@dataclass
class ORBResult:
    refined_row_in_chip: float
    refined_col_in_chip: float
    angle_deg: float
    good_matches: int
    inliers: int
    homography: list[list[float]]


def estimate_pixel_size_m(ds: rasterio.io.DatasetReader) -> tuple[float, float]:
    rx, ry = ds.res
    return abs(float(rx)), abs(float(ry))


def meters_to_pixels(ds: rasterio.io.DatasetReader, width_m: float, height_m: float) -> tuple[int, int]:
    px_w_m, px_h_m = estimate_pixel_size_m(ds)
    w_px = max(1, int(round(width_m / px_w_m)))
    h_px = max(1, int(round(height_m / px_h_m)))
    return w_px, h_px


def centered_window(row: float, col: float, height_px: int, width_px: int, max_rows: int, max_cols: int) -> Window:
    r0 = int(round(row - height_px / 2))
    c0 = int(round(col - width_px / 2))
    r1 = r0 + height_px
    c1 = c0 + width_px

    r0 = max(0, r0)
    c0 = max(0, c0)
    r1 = min(max_rows, r1)
    c1 = min(max_cols, c1)

    h = r1 - r0
    w = c1 - c0
    if h < height_px:
        r0 = max(0, r1 - height_px)
        r1 = min(max_rows, r0 + height_px)
    if w < width_px:
        c0 = max(0, c1 - width_px)
        c1 = min(max_cols, c0 + width_px)

    return Window(col_off=c0, row_off=r0, width=c1 - c0, height=r1 - r0)


def latlon_to_mapxy(ds: rasterio.io.DatasetReader, lat: float, lon: float) -> tuple[float, float]:
    transformer = Transformer.from_crs("EPSG:4326", ds.crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return float(x), float(y)


def mapxy_to_rowcol(ds: rasterio.io.DatasetReader, x: float, y: float) -> tuple[int, int]:
    r, c = rowcol(ds.transform, x, y)
    return int(r), int(c)


def pixel_to_mapxy(ds: rasterio.io.DatasetReader, row: float, col: float) -> tuple[float, float]:
    x, y = xy(ds.transform, row, col, offset="center")
    return float(x), float(y)


def stretch_to_uint8(img: np.ndarray) -> np.ndarray:
    arr = np.asarray(img)
    if arr.dtype == np.uint8:
        return arr

    if arr.ndim == 2:
        arr = arr[:, :, None]

    out = np.zeros_like(arr, dtype=np.uint8)
    for b in range(arr.shape[2]):
        band = arr[:, :, b].astype(np.float32)
        finite = np.isfinite(band)
        if not finite.any():
            continue
        vals = band[finite]
        lo = np.percentile(vals, 2)
        hi = np.percentile(vals, 98)
        if hi <= lo:
            hi = lo + 1.0
        scaled = np.clip((band - lo) * 255.0 / (hi - lo), 0, 255)
        out[:, :, b] = scaled.astype(np.uint8)

    if out.shape[2] == 1:
        return out[:, :, 0]
    return out


def read_raster_for_cv(ds: rasterio.io.DatasetReader, window: Window | None = None) -> np.ndarray:
    if ds.count >= 3:
        arr = ds.read([1, 2, 3], window=window)
        img = np.transpose(arr, (1, 2, 0))
    elif ds.count == 1:
        arr = ds.read(1, window=window)
        img = arr[:, :, None]
    else:
        raise RuntimeError(f"Unsupported raster band count: {ds.count}")

    img = stretch_to_uint8(img)
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 1:
        img = cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2BGR)

    return img


def load_camera_image(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Failed to load camera image: {path}")
    return img


def downsample_keep_aspect(img: np.ndarray, max_dim: int = 1024) -> tuple[np.ndarray, float]:
    h, w = img.shape[:2]
    scale = min(max_dim / max(h, w), 1.0)
    if scale == 1.0:
        return img, 1.0
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    out = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return out, scale


def preprocess_for_orb(img_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def orb_refine(
    camera_bgr: np.ndarray,
    mapchip_bgr: np.ndarray,
    ratio_thresh: float = 0.75,
    min_good: int = 40,
    min_inliers: int = 20,
    camera_max_dim: int = 960,
    mapchip_max_dim: int = 1400,
) -> ORBResult | None:
    cam_small, _ = downsample_keep_aspect(camera_bgr, max_dim=camera_max_dim)
    map_small, map_scale = downsample_keep_aspect(mapchip_bgr, max_dim=mapchip_max_dim)

    cam_gray = preprocess_for_orb(cam_small)
    map_gray = preprocess_for_orb(map_small)

    orb = cv2.ORB_create(
        nfeatures=5000,
        scaleFactor=1.2,
        nlevels=8,
        edgeThreshold=31,
        patchSize=31,
        fastThreshold=10,
    )

    kp1, des1 = orb.detectAndCompute(cam_gray, None)
    kp2, des2 = orb.detectAndCompute(map_gray, None)

    if des1 is None or des2 is None:
        return None
    if len(kp1) < 20 or len(kp2) < 20:
        return None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    knn = bf.knnMatch(des1, des2, k=2)

    good = []
    for pair in knn:
        if len(pair) != 2:
            continue
        m, n = pair
        if m.distance < ratio_thresh * n.distance:
            good.append(m)

    if len(good) < min_good:
        return None

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None or mask is None:
        return None

    inliers = int(mask.sum())
    if inliers < min_inliers:
        return None

    h, w = cam_gray.shape
    center = np.array([[[w / 2.0, h / 2.0]]], dtype=np.float32)
    xaxis = np.array([[[w / 2.0 + 100.0, h / 2.0]]], dtype=np.float32)

    center_map = cv2.perspectiveTransform(center, H)[0, 0]
    xaxis_map = cv2.perspectiveTransform(xaxis, H)[0, 0]

    angle_deg = float(np.degrees(np.arctan2(
        xaxis_map[1] - center_map[1],
        xaxis_map[0] - center_map[0]
    )))

    refined_col = float(center_map[0] / map_scale)
    refined_row = float(center_map[1] / map_scale)

    return ORBResult(
        refined_row_in_chip=refined_row,
        refined_col_in_chip=refined_col,
        angle_deg=angle_deg,
        good_matches=len(good),
        inliers=inliers,
        homography=H.tolist(),
    )


def clamp_refinement_distance(
    gps_x: float,
    gps_y: float,
    refined_x: float,
    refined_y: float,
    max_distance_m: float,
) -> tuple[float, float, float, bool]:
    dist = math.hypot(refined_x - gps_x, refined_y - gps_y)
    accepted = dist <= max_distance_m
    return refined_x, refined_y, dist, accepted


def crop_dataset_to_geotiff(
    ds: rasterio.io.DatasetReader,
    center_x: float,
    center_y: float,
    crop_width_m: float,
    crop_height_m: float,
    out_path: str,
) -> dict:
    center_row, center_col = mapxy_to_rowcol(ds, center_x, center_y)
    crop_w_px, crop_h_px = meters_to_pixels(ds, crop_width_m, crop_height_m)
    win = centered_window(center_row, center_col, crop_h_px, crop_w_px, ds.height, ds.width)

    data = ds.read(window=win, boundless=True, fill_value=ds.nodata)
    out_transform = window_transform(win, ds.transform)

    profile = ds.profile.copy()
    profile.update(
        height=data.shape[1],
        width=data.shape[2],
        transform=out_transform,
    )

    with rasterio.open(out_path, "w", **profile) as out_ds:
        out_ds.write(data)

    return {
        "window_row_off": float(win.row_off),
        "window_col_off": float(win.col_off),
        "window_width_px": int(win.width),
        "window_height_px": int(win.height),
        "center_row": center_row,
        "center_col": center_col,
        "output_path": str(Path(out_path).resolve()),
    }


def localize_and_crop(
    *,
    ortho_path: str,
    dsm_path: str,
    camera_path: str,
    gps_lat: float,
    gps_lon: float,
    coarse_search_m: float = 120.0,
    final_crop_m: float = 40.0,
    orb_ratio_thresh: float = 0.75,
    orb_min_good: int = 40,
    orb_min_inliers: int = 20,
    camera_max_dim: int = 960,
    mapchip_max_dim: int = 1400,
    max_refinement_shift_m: float = 60.0,
    require_orb: bool = False,
    out_dsm: str = "cropped_dsm.tif",
) -> dict:
    camera_bgr = load_camera_image(camera_path)

    with rasterio.open(ortho_path) as ortho_ds, rasterio.open(dsm_path) as dsm_ds:
        if ortho_ds.crs is None:
            raise RuntimeError("Orthophoto CRS is missing")
        if dsm_ds.crs is None:
            raise RuntimeError("DSM CRS is missing")

        gps_x_ortho, gps_y_ortho = latlon_to_mapxy(ortho_ds, gps_lat, gps_lon)
        gps_row_ortho, gps_col_ortho = mapxy_to_rowcol(ortho_ds, gps_x_ortho, gps_y_ortho)

        coarse_w_px, coarse_h_px = meters_to_pixels(ortho_ds, coarse_search_m, coarse_search_m)
        coarse_win = centered_window(
            gps_row_ortho, gps_col_ortho,
            coarse_h_px, coarse_w_px,
            ortho_ds.height, ortho_ds.width,
        )

        ortho_chip = read_raster_for_cv(ortho_ds, window=coarse_win)

        final_x_ortho = gps_x_ortho
        final_y_ortho = gps_y_ortho
        confidence = "gps_only"
        orb_meta = None

        orb = orb_refine(
            camera_bgr=camera_bgr,
            mapchip_bgr=ortho_chip,
            ratio_thresh=orb_ratio_thresh,
            min_good=orb_min_good,
            min_inliers=orb_min_inliers,
            camera_max_dim=camera_max_dim,
            mapchip_max_dim=mapchip_max_dim,
        )

        if orb is not None:
            refined_row_ortho = float(coarse_win.row_off + orb.refined_row_in_chip)
            refined_col_ortho = float(coarse_win.col_off + orb.refined_col_in_chip)
            candidate_x_ortho, candidate_y_ortho = pixel_to_mapxy(ortho_ds, refined_row_ortho, refined_col_ortho)

            _, _, refinement_dist_m, accepted = clamp_refinement_distance(
                gps_x_ortho, gps_y_ortho,
                candidate_x_ortho, candidate_y_ortho,
                max_refinement_shift_m,
            )

            orb_meta = asdict(orb)
            orb_meta["refinement_distance_m"] = refinement_dist_m
            orb_meta["accepted_by_distance_gate"] = accepted

            if accepted:
                final_x_ortho = candidate_x_ortho
                final_y_ortho = candidate_y_ortho
                confidence = "orb_refined"
            elif require_orb:
                raise RuntimeError("ORB refinement exceeded shift gate and require_orb=True")

        elif require_orb:
            raise RuntimeError("ORB refinement failed and require_orb=True")

        if ortho_ds.crs != dsm_ds.crs:
            transformer = Transformer.from_crs(ortho_ds.crs, dsm_ds.crs, always_xy=True)
            final_x_dsm, final_y_dsm = transformer.transform(final_x_ortho, final_y_ortho)
        else:
            final_x_dsm, final_y_dsm = final_x_ortho, final_y_ortho

        dsm_crop_meta = crop_dataset_to_geotiff(
            ds=dsm_ds,
            center_x=float(final_x_dsm),
            center_y=float(final_y_dsm),
            crop_width_m=final_crop_m,
            crop_height_m=final_crop_m,
            out_path=out_dsm,
        )

        return {
            "confidence": confidence,
            "gps_prior": {
                "lat": gps_lat,
                "lon": gps_lon,
                "ortho_x": gps_x_ortho,
                "ortho_y": gps_y_ortho,
                "ortho_row": gps_row_ortho,
                "ortho_col": gps_col_ortho,
            },
            "ortho_final_xy": {
                "x": float(final_x_ortho),
                "y": float(final_y_ortho),
            },
            "dsm_final_xy": {
                "x": float(final_x_dsm),
                "y": float(final_y_dsm),
            },
            "orb": orb_meta,
            "dsm_crop": dsm_crop_meta,
        }