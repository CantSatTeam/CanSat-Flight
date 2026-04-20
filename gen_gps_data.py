import math
import time
import random
from datetime import datetime, timedelta

def decimal_to_nmea(coord, is_lat=True):
    degrees = int(abs(coord))
    minutes = (abs(coord) - degrees) * 60
    if is_lat:
        return f"{degrees:02d}{minutes:06.3f}", "N" if coord >= 0 else "S"
    else:
        return f"{degrees:03d}{minutes:06.3f}", "E" if coord >= 0 else "W"

def checksum(sentence):
    cs = 0
    for c in sentence:
        cs ^= ord(c)
    return f"*{cs:02X}"

def move(lat, lon, speed_mps, heading_deg, dt=1.0):
    R = 6378137  # Earth radius in meters
    d = speed_mps * dt

    heading = math.radians(heading_deg)

    dlat = d * math.cos(heading) / R
    dlon = d * math.sin(heading) / (R * math.cos(math.radians(lat)))

    lat += math.degrees(dlat)
    lon += math.degrees(dlon)

    return lat, lon

# Initial position (example: Edmonton-ish)
lat = 53.5461
lon = -113.4938
alt = 670.0

speed = 5.0  # m/s (~18 km/h)
heading = 90.0  # east

t = datetime.utcnow()

with open("gps_data.txt", "w") as f:
    for _ in range(300):  # 5 minutes at 1 Hz
        # small random variation
        speed += random.uniform(-0.2, 0.2)
        heading += random.uniform(-2, 2)

        lat, lon = move(lat, lon, speed, heading)

        lat_nmea, lat_dir = decimal_to_nmea(lat, True)
        lon_nmea, lon_dir = decimal_to_nmea(lon, False)

        time_str = t.strftime("%H%M%S")
        date_str = t.strftime("%d%m%y")

        fix_quality = 1
        sats = random.randint(6, 10)
        hdop = round(random.uniform(0.8, 1.5), 1)

        # GGA
        gga_body = f"GPGGA,{time_str},{lat_nmea},{lat_dir},{lon_nmea},{lon_dir},{fix_quality},{sats},{hdop},{alt:.1f},M,0.0,M,,"
        gga = f"${gga_body}{checksum(gga_body)}"

        # RMC
        speed_knots = speed * 1.94384
        rmc_body = f"GPRMC,{time_str},A,{lat_nmea},{lat_dir},{lon_nmea},{lon_dir},{speed_knots:.2f},{heading:.2f},{date_str},,,A"
        rmc = f"${rmc_body}{checksum(rmc_body)}"

        f.write(gga + "\n")
        f.write(rmc + "\n")

        t += timedelta(seconds=1)