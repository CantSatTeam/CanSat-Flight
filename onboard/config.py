LOG_PATH = "logs/primary_log.txt"

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
CAMERA_DIR = "onboard/pics" #/home/couldntsat/CanSat-Flight/

# Geocrop
GEOCROP_ENABLED = True
GEOCROP_USE_ORB = False
GEOCROP_REQUIRE_ORB = False

GEOCROP_ORTHO_PATH = "/home/couldntsat/CanSat-Flight/maps/orthophoto.tif"
GEOCROP_DSM_PATH = "/home/couldntsat/CanSat-Flight/maps/dsm.tif"
GEOCROP_OUTPUT_DIR = "/home/couldntsat/CanSat-Flight/crops"

GEOCROP_MAX_GPS_AGE_S = 15.0
GEOCROP_COARSE_SEARCH_M = 80.0
GEOCROP_FINAL_CROP_M = 30.0
GEOCROP_MAX_REFINEMENT_SHIFT_M = 35.0

GEOCROP_ORB_RATIO_THRESH = 0.75
GEOCROP_ORB_MIN_GOOD = 30
GEOCROP_ORB_MIN_INLIERS = 15
GEOCROP_ORB_NFEATURES = 1500
GEOCROP_CAMERA_MAX_DIM = 640
GEOCROP_MAPCHIP_MAX_DIM = 1024

# Inference
INFERENCE_ENABLED = True

INFERENCE_PY311 = "/home/couldntsat/CanSat-MHE/terrainmesh/env/bin/python"
INFERENCE_WORKER = "/home/couldntsat/CanSat-MHE/terrainmesh/infer_worker.py"

INFERENCE_OUTPUT_DIR = "/home/couldntsat/CanSat-Flight/data/inference"
INFERENCE_TIMEOUT_S = 180
INFERENCE_POLL_S = 0.5
INFERENCE_RETRY_S = 5.0

INFERENCE_LATEST_ONLY = True