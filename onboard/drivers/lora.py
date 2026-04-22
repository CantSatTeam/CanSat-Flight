from dataclasses import dataclass
import serial
from config import *

@dataclass
class LoRaHandle:
    serial_port: object


def init_lora() -> LoRaHandle:
    """
    Initialize E22 UART interface.

    Assumes the module is already configured for transparent transmission mode.
    """
    ser = serial.Serial(
        port=LORA_UART_PORT,
        baudrate=LORA_BAUDRATE,
        timeout=LORA_TIMEOUT_S,
        write_timeout=LORA_WRITE_TIMEOUT_S,
    )

    if hasattr(ser, "reset_input_buffer"):
        ser.reset_input_buffer()
    if hasattr(ser, "reset_output_buffer"):
        ser.reset_output_buffer()

    return LoRaHandle(serial_port=ser)


def transmit_lora_transparent(lora_handle: LoRaHandle, payload: str) -> None:
    if not isinstance(payload, str):
        raise TypeError("payload must be a string")

    wire = payload.encode("utf-8")
    wire += b"\n"

    if len(wire) > LORA_MAX_PAYLOAD_BYTES:
        raise ValueError(
            f"LoRa payload too large: {len(wire)} bytes > {LORA_MAX_PAYLOAD_BYTES}"
        )

    written = lora_handle.serial_port.write(wire)
    lora_handle.serial_port.flush()

    if written != len(wire):
        raise RuntimeError(
            f"Incomplete radio write: wrote {written} of {len(wire)} bytes"
        )


def close_lora(lora_handle: LoRaHandle) -> None:
    try:
        lora_handle.serial_port.close()
    except Exception:
        pass