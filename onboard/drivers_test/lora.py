from dataclasses import dataclass, field


@dataclass
class LoRaHandle:
    sent_payloads: list[str] = field(default_factory=list)
    closed: bool = False


def init_lora() -> LoRaHandle:
    return LoRaHandle()


def transmit_lora_transparent(lora_handle: LoRaHandle, payload: str) -> None:
    if lora_handle.closed:
        raise RuntimeError("Fake LoRa is closed")

    if not isinstance(payload, str):
        raise TypeError("payload must be a string")

    lora_handle.sent_payloads.append(payload)


def close_lora(lora_handle: LoRaHandle) -> None:
    lora_handle.closed = True


def get_transmit_count(lora_handle: LoRaHandle) -> int:
    return len(lora_handle.sent_payloads)


def get_last_payload(lora_handle: LoRaHandle):
    if not lora_handle.sent_payloads:
        return None
    return lora_handle.sent_payloads[-1]