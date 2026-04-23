import time
import serial

# adjust port if needed: '/dev/serial0' is typical on Raspberry Pi
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
time.sleep(0.1)  # allow port to settle

message = b'Hello LoRa!\n'
ser.write(message)

# optional: read any immediate response
time.sleep(0.1)
resp = ser.read(ser.in_waiting or 64)
print('RX:', resp)

ser.close()
