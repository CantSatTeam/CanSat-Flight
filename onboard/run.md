bme280:
1. enable i2c on pi: raspi-config -> interface options -> i2c -> enable
    sudo raspi-config
2. run `pip install smbus2 bme280`

lora:
1. (DO NOT RUN THIS IS CIRCUITPYTHON WOULD NEED BLINKA) pip install ebyte-lora-e22-circuitpython

neo:
1. enable serial port on pi: raspi-config -> interface options -> serial -> disable login shell over serial (x), enable serial port (check)
    sudo raspi-config
2. add user to serial group
    sudo usermod -a -G dialout $USER
3. log out and back in, verify with groups/id
4. check:
    ls -l /dev/serial*        # shows /dev/serial0 -> actual device
    readlink -f /dev/serial0  # shows the real device path
    sudo cat /dev/serial0     # raw NMEA stream (or use `screen /dev/serial0 9600`)
5. run `pip install pyserial pynmea2`

camera
