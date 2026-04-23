from utils.geocrop_core import localize_and_crop

meta = localize_and_crop(
    ortho_path="/home/couldntsat/CanSat-Flight/maps/orthophoto.tif",   # not used in GPS-only mode
    dsm_path="/home/couldntsat/CanSat-Flight/maps/dsm.tif",
    camera_path="/home/couldntsat/CanSat-Flight/maps/test.jpg",  # harmless, but ignored
    gps_lat=49.442575,
    gps_lon=-112.009654,
    use_orb=False,
    final_crop_m=300.0,
    out_dsm="/home/couldntsat/CanSat-Flight/crops/test_crop.tif",
)

print(meta)