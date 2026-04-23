#!/usr/bin/env python3
"""Query EBYTE E22-T module settings using AT commands.

Notes:
- Put the module into Configuration Mode (M1=1, M0=0) before running, or enable software switch
  if your firmware supports it.
- Configuration mode serial settings: 9600 8N1 (per manual).
"""
import argparse
import time
import sys

try:
    import serial
    from serial.tools import list_ports
except Exception as e:
    print('pyserial required: pip3 install pyserial', file=sys.stderr)
    raise


DEFAULT_COMMANDS = [
    'AT+DEVTYPE=?',
    'AT+FWCODE=?',
    'AT+ADDR=?',
    'AT+NETID=?',
    'AT+CHANNEL=?',
    'AT+MODE=?',
    'AT+UAUX=?',
    'AT+SWITCH=?',
]


def list_serial():
    ports = list(list_ports.comports())
    if not ports:
        print('No serial ports found')
        return
    for p in ports:
        print(f'{p.device} - {p.description}')


def send_cmd(ser, cmd: str, read_timeout=0.5):
    payload = (cmd + '\r\n').encode('ascii')
    ser.write(payload)
    ser.flush()
    # collect responses for a short time
    deadline = time.time() + read_timeout
    lines = []
    while time.time() < deadline:
        line = ser.readline()
        if not line:
            break
        try:
            lines.append(line.decode('utf-8', errors='replace').strip())
        except Exception:
            lines.append(repr(line))
    return lines


def query(port: str, baud: int, commands, inter=0.05):
    with serial.Serial(port, baudrate=baud, timeout=0.2) as ser:
        print(f'Opened {port} @ {baud}bps')
        time.sleep(0.1)
        for cmd in commands:
            print(f'>>> {cmd}')
            lines = send_cmd(ser, cmd)
            if not lines:
                print('(no response)')
            else:
                for l in lines:
                    print(l)
            time.sleep(inter)


def main():
    p = argparse.ArgumentParser(description='Query E22-T via AT commands')
    p.add_argument('--list', action='store_true', help='List serial ports and exit')
    p.add_argument('--port', '-p', default='/dev/serial0', help='Serial device')
    p.add_argument('--baud', '-b', type=int, default=9600, help='Baud rate (config mode 9600)')
    p.add_argument('--cmd', '-c', action='append', help='Extra AT command to send (may be repeated)')
    p.add_argument('--timeout', '-t', type=float, default=0.5, help='Per-command read timeout seconds')
    args = p.parse_args()

    if args.list:
        list_serial()
        return

    print('Warning: ensure module is in Configuration Mode (M1=1 M0=0)')
    query_cmds = list(DEFAULT_COMMANDS)
    if args.cmd:
        query_cmds.extend(args.cmd)

    try:
        query(args.port, args.baud, query_cmds)
    except serial.SerialException as e:
        print('Serial error:', e, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
