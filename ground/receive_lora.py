# MicroPython receiver for Raspberry Pi Pico (RP2040)
# Connect E22-T TX -> Pico RX (GP1), E22-T RX -> Pico TX (GP0), common GND
# Put module in transparent Mode 0 (M1=0 M0=0) to receive raw payloads.

import machine
import time


def format_bytes(b):
    # b is a bytes-like object
    try:
        text = b.decode('utf-8')
    except Exception:
        try:
            text = b.decode('latin-1')
        except Exception:
            text = str(b)
    hexs = ' '.join('{:02X}'.format(x) for x in b)
    return "text={} | hex={}".format(repr(text), hexs)


def main():
    # Use UART0 with TX=GP0, RX=GP1 (change pins below if you wired differently)
    tx_pin = machine.Pin(0)
    rx_pin = machine.Pin(1)
    uart = machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=tx_pin, rx=rx_pin)

    print('Listening on UART0 (TX=GP0 RX=GP1) @ 9600bps. Ctrl-C to stop.')
    try:
        while True:
            available = uart.any()
            if available:
                data = uart.read(available)
                if not data:
                    time.sleep_ms(10)
                    continue
                ts = time.ticks_ms() / 1000.0
                entry = '[{:.3f}] {}'.format(ts, format_bytes(data))
                print(entry)
            else:
                time.sleep_ms(20)
    except KeyboardInterrupt:
        print('\nStopped by user')


if __name__ == '__main__':
    main()
