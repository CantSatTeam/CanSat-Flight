#!/usr/bin/env python3
"""Simple LoRa receiver for E22-T series using pyserial.

Usage:
  python3 ground/receive_lora.py --port /dev/serial0 --baud 9600

Reads bytes from the serial port and prints timestamped messages.
"""
import argparse
import serial
import time
import sys


def open_serial(port: str, baud: int, timeout: float = 1.0):
    return serial.Serial(port, baudrate=baud, timeout=timeout)


def format_bytes(b: bytes) -> str:
    try:
        text = b.decode('utf-8', errors='replace')
    except Exception:
        text = repr(b)
    hexs = ' '.join(f'{x:02X}' for x in b)
    return f"text={text!r} | hex={hexs}"


def run(port: str, baud: int, logfile: str | None):
    ser = open_serial(port, baud)
    print(f'Listening on {port} @ {baud}bps. Ctrl-C to exit.')
    out = None
    if logfile:
        out = open(logfile, 'a', buffering=1)
        print(f'Logging to {logfile}')

    try:
        while True:
            # read any available bytes; adjust behavior if you prefer line-based reads
            data = ser.read(ser.in_waiting or 1)
            if not data:
                time.sleep(0.02)
                continue
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            entry = f"[{ts}] {format_bytes(data)}"
            print(entry)
            if out:
                out.write(entry + '\n')
    except KeyboardInterrupt:
        print('\nExiting.')
    finally:
        ser.close()
        if out:
            out.close()


def main():
    p = argparse.ArgumentParser(description='Receive LoRa messages (E22-T) over serial')
    p.add_argument('--port', '-p', default='/dev/serial0', help='Serial device')
    p.add_argument('--baud', '-b', type=int, default=9600, help='Serial baud rate (default 9600)')
    p.add_argument('--log', '-l', help='Append received messages to logfile')
    args = p.parse_args()

    try:
        run(args.port, args.baud, args.log)
    except serial.SerialException as e:
        print('Serial error:', e, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
