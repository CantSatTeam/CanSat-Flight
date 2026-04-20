### GPS Sensor Code
### no reference right now

import serial
import pynmea2

### Pins ###

# afaik these are not actually needed for the code
# but here they are
GPS_TX = 14 # GPIO14
GPS_RX = 15 # GPIO15

### GPS Initialization ###

# Adjust port if needed
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

### Main Loop ###

while True:
    line = ser.readline().decode('utf-8', errors='ignore').strip()

    if line.startswith('$G'):
        try:
            msg = pynmea2.parse(line)

            if isinstance(msg, pynmea2.types.talker.GGA):
                print("Lat:", msg.latitude)
                print("Lon:", msg.longitude)
                print("Alt:", msg.altitude)

            elif isinstance(msg, pynmea2.types.talker.RMC):
                print("Time:", msg.timestamp)
                print("Speed:", msg.spd_over_grnd)

        except pynmea2.ParseError:
            pass
