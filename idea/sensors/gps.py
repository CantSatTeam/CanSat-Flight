import serial
import pynmea2

class FakeSerial:
    def __init__(self, path):
        self.f = open(path, 'r')

    def readline(self):
        line = self.f.readline()
        return line.encode('ascii') if line else b''

ser = FakeSerial('gps_data.txt')

# ser = serial.Serial('/dev/serial0', 9600, timeout=1)

while True:
    raw = ser.readline()
    if not raw:
        break  # EOF reached

    line = raw.decode('ascii', errors='replace').strip()

    if line.startswith('$'):
        try:
            msg = pynmea2.parse(line)

            if isinstance(msg, pynmea2.types.talker.GGA):
                print(msg.latitude, msg.longitude)

        except pynmea2.ParseError:
            pass