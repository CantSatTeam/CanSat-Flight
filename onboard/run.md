bme280:
1. enable i2c on pi: raspi-config -> interface options -> i2c -> enable
sudo raspi-config 
2. run `pip install smbus2 bme280`

lora:
1. (DO NOT RUN THIS IS CIRCUITPYTHON WOULD NEED BLINKA) pip install ebyte-lora-e22-circuitpython
