LOG_PATH = "onboard/logs/primary_log.txt"

# Sensor / service rates
TELEMETRY_HZ = 1.0
BME_HZ = 1.0
QUEUE_SIZE = 32

# BME280
BME_PORT = 1
BME_ADDRESS = 0x76

# LoRa / E22 UART
LORA_ENABLED = True
LORA_UART_PORT = "/dev/serial0"     # or /dev/ttyS0 or /dev/ttyAMA0
LORA_BAUDRATE = 9600
LORA_TIMEOUT_S = 0.2
LORA_WRITE_TIMEOUT_S = 0.2
LORA_RETRY_S = 2.0

# Keep payloads small for radio reliability
LORA_MAX_PAYLOAD_BYTES = 240

# GPS UART
GPS_UART_PORT = "/dev/ttyAMA0"   # must be different from LORA_UART_PORT
GPS_BAUDRATE = 9600
GPS_TIMEOUT_S = 0.2
GPS_RETRY_S = 2.0

# Camera
CAMERA_INTERVAL = 5.0
CAMERA_DIR = "onboard/pics"
