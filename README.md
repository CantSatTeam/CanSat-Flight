Part of the Couldn'tSat team's soon-to-be [submission](https://github.com/CantSatTeam/CanSat2026) to the [2026 CSDCMS CanSat Competition](https://www.csdcms.ca/CanSat_info.html).

# CanSat Flight Software

Flight and ground-station software for **Couldn’tSat**, developed for the **2026 CSDCMS CanSat Design Challenge**.

Our CanSat was built around two missions:

* **Primary mission:** collect environmental and positional telemetry during descent and transmit it to a ground station at 1 Hz.
* **Secondary mission:** perform **Monocular Height Estimation (MHE) onboard a Raspberry Pi 5**, reconstructing 3D terrain from downward-facing aerial imagery without relying on a ground computer or cloud processing.

This repository contains the **real-time flight software and ground communication system**. The corresponding ML model, training-data pipeline, and TerrainMesh adaptation are available in [CanSat-MHE](https://github.com/CantSatTeam/CanSat-MHE).

## System Architecture

The onboard software uses a **multithreaded service architecture** designed to prevent expensive or unreliable operations from blocking mission-critical tasks.

Independent services handle:

* BME280 temperature, pressure, and humidity sampling
* GPS acquisition
* LoRa telemetry
* onboard logging
* downward-facing camera capture
* terrain-input localization and geocropping
* MHE inference
* system health monitoring

Services communicate through **shared mission state and bounded queues**. This allows telemetry and sensor sampling to continue independently while more computationally expensive operations such as image processing and neural-network inference are running.

```text
                 +----------------+
                 |  Sensors / GPS |
                 +-------+--------+
                         |
                         v
                +------------------+
                | Shared Flight    |
                | Mission State    |
                +---+----------+---+
                    |          |
          +---------+          +-------------+
          v                                  v
+------------------+                +------------------+
| Telemetry / LoRa |                | Camera Capture   |
| Logging          |                +--------+---------+
+------------------+                         |
                                             v
                                    +------------------+
                                    | Terrain / DSM    |
                                    | Localization     |
                                    +--------+---------+
                                             |
                                             v
                                    +------------------+
                                    | TerrainMesh MHE  |
                                    | Inference        |
                                    +------------------+
```

## Onboard Terrain Estimation

Raw camera images are far too large to reliably transmit over the CanSat's low-bandwidth radio link, so terrain reconstruction is performed **locally on the Raspberry Pi 5**.

During descent, the flight system captures aerial imagery and pairs it with a sparse terrain prior used by **TerrainMesh**, a graph-based MHE model. GPS information is used to select the corresponding region of the preloaded terrain data before it is passed to the inference pipeline.

The resulting terrain reconstruction is stored onboard for recovery.

Performing inference onboard:

* avoids transmitting high-resolution imagery over LoRa
* reduces dependence on the ground station
* allows terrain estimation to continue even if radio communication fails
* demonstrates deployment of a research ML system on a resource-constrained aerial platform

## Reliability

The flight software was designed around the assumption that individual components may become slow, unavailable, or produce invalid data during flight.

The system includes:

* bounded queues to prevent telemetry backlogs
* automatic radio reconnection
* freshness checks for GPS and sensor data
* watchdog monitoring for stale subsystems
* health flags shared across services
* inference timeouts and exception isolation
* image validation before inference
* rejection of dark, blank, or invalid camera/depth inputs

This keeps critical sensing and telemetry independent from optional or computationally intensive workloads.

## Telemetry

Environmental and positional data are packaged into compact packets and transmitted through an **E22 LoRa radio**.

Telemetry includes:

* temperature
* atmospheric pressure
* humidity
* GPS position and altitude
* GPS time
* subsystem health information

The ground-station software receives these packets for monitoring and storage during flight.

## Hardware

* **Raspberry Pi 5** — flight computer and onboard ML inference
* **Raspberry Pi Camera** — downward-facing aerial imagery
* **BME280** — temperature, pressure, and humidity
* **NEO-series GPS** — localization and recovery
* **E22 LoRa radio** — CanSat-to-ground telemetry

## Repository Structure

```text
onboard/
├── drivers/        # Hardware interfaces
├── services/
│   ├── camera.py
│   ├── geocrop.py
│   ├── inference.py
│   ├── logger.py
│   ├── sampler.py
│   ├── telemetry.py
│   └── watchdog.py
├── data/           # Shared mission state / packet structures
├── utils/          # Geospatial and supporting utilities
├── config.py       # Hardware and service configuration
└── main.py         # Flight-system orchestration

ground/
├── main.py
├── query_lora.py
└── receive_lora.py

gen_gps_data.py     # GPS simulation/testing utility
```

## Related Repository

**[CanSat-MHE](https://github.com/CantSatTeam/CanSat-MHE)** contains the other half of the project: the TerrainMesh model, training-data preparation, domain adaptation, GSD handling, and augmentations developed to make MHE more robust to CanSat flight conditions.

