import queue
import time

from config import *
import drivers.lora as lora
from data.packets import TelemetryFrame


def put_latest(q: queue.Queue, item) -> None:
    """
    Non-blocking queue write.
    If full, drop oldest and keep newest.
    """
    try:
        q.put_nowait(item)
    except queue.Full:
        try:
            q.get_nowait()
        except queue.Empty:
            pass
        q.put_nowait(item)


def format_packet_csv(frame: TelemetryFrame) -> str:
    """
    Compact CSV:
    seq,monotonic,temp_x10,press_x10,hum_x10,gps_valid,lat_1e5,lon_1e5,alt_dm,gps_time,bme_ok,gps_ok,radio_ok
    
    multiplies to keep as integers for compactness
    """
    temp_x10 = round(frame.ambient_temp_c * 10)
    press_x10 = round(frame.pressure_hpa * 10)
    hum_x10 = round(frame.humidity_pct * 10)

    lat_1e5 = "" if frame.lat_deg is None else round(frame.lat_deg * 1e5)
    lon_1e5 = "" if frame.lon_deg is None else round(frame.lon_deg * 1e5)
    alt_dm = "" if frame.alt_m is None else round(frame.alt_m * 10)
    
    print(f"""
          [TELEM] Frame {frame.seq}:
          temp={temp_x10/10}C press={press_x10/10}hPa hum={hum_x10/10}%
          gps_valid={frame.gps_valid} lat={lat_1e5/1e5 if lat_1e5 != '' else 'N/A'} lon={lon_1e5/1e5 if lon_1e5 != '' else 'N/A'} alt={alt_dm/10 if alt_dm != '' else 'N/A'}m gps_time={frame.gps_time_utc}
          bme_ok={frame.bme_ok} gps_ok={frame.gps_ok} radio_ok={frame.radio_ok}
          """)

    return (
        f"{frame.seq},"
        f"{frame.monotonic_s:.2f},"
        f"{temp_x10},{press_x10},{hum_x10},"
        f"{frame.gps_valid},"
        f"{lat_1e5},{lon_1e5},{alt_dm},"
        f"{frame.gps_time_utc},"
        f"{frame.bme_ok},{frame.gps_ok},{frame.radio_ok}"
    )


def telemetry_task(stop_event, state, radio_queue: queue.Queue, log_queue: queue.Queue):
    seq = 0
    period = 1.0 / TELEMETRY_HZ
    next_t = time.monotonic()

    while not stop_event.is_set():
        bme, gps, health = state.snapshot()

        if bme is not None:
            gps_valid = 1 if (gps is not None and gps.fix_ok) else 0

            frame = TelemetryFrame(
                seq=seq,
                monotonic_s=time.monotonic(),
                ambient_temp_c=bme.ambient_temp_c,
                pressure_hpa=bme.pressure_hpa,
                humidity_pct=bme.humidity_pct,
                gps_valid=gps_valid,
                lat_deg=(gps.lat_deg if gps_valid else None),
                lon_deg=(gps.lon_deg if gps_valid else None),
                alt_m=(gps.alt_m if gps_valid else None),
                gps_time_utc=(gps.utc_time_str if gps_valid else ""),
                bme_ok=int(bool(health["bme_ok"])),
                gps_ok=int(bool(health["gps_ok"])),
                radio_ok=int(bool(health["radio_ok"])),
            )

            packet = format_packet_csv(frame)

            put_latest(radio_queue, packet)
            put_latest(log_queue, packet)

            state.set_health_flag("last_telem_s", time.monotonic())
            seq += 1
        else:
            print("[TELEM] No BME data yet; skipping packet")

        next_t += period
        delay = max(0.0, next_t - time.monotonic())
        stop_event.wait(delay)


def radio_task(stop_event, state, radio_queue: queue.Queue):
    """
    Dedicated TX worker.
    Keeps retrying if the UART/radio fails.
    """
    if not LORA_ENABLED:
        print("[RADIO] Disabled in config")
        state.set_health_flag("radio_ok", False)
        while not stop_event.is_set():
            stop_event.wait(1.0)
        return

    lora_handle = None
    last_init_attempt_s = 0.0

    while not stop_event.is_set():
        if lora_handle is None:
            now = time.monotonic()
            if now - last_init_attempt_s >= LORA_RETRY_S:
                last_init_attempt_s = now
                try:
                    lora_handle = lora.init_lora()
                    state.set_health_flag("radio_ok", True)
                    print("[RADIO] E22 UART ready")
                except Exception as e:
                    state.set_health_flag("radio_ok", False)
                    print(f"[RADIO INIT ERROR] {e}")
            stop_event.wait(0.2)
            continue

        try:
            packet = radio_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        try:
            lora.transmit_lora_transparent(lora_handle, packet)
            state.set_health_flag("radio_ok", True)
            state.set_health_flag("last_radio_s", time.monotonic())
            print(f"[RADIO TX] {packet}")
        except Exception as e:
            state.set_health_flag("radio_ok", False)
            print(f"[RADIO ERROR] {e}")
            lora.close_lora(lora_handle)
            lora_handle = None

    if lora_handle is not None:
        lora.close_lora(lora_handle)