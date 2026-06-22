# VSLAM-UAV

> GPS-Denied Autonomous UAV Navigation using Visual SLAM & VIO

Dockerized pipeline for real-time Visual SLAM on NVIDIA Jetson Orin, enabling fully autonomous GPS-denied flight using stereo-inertial odometry from Intel RealSense D435i and NVIDIA Isaac ROS cuVSLAM.

---

## System Architecture

```
 ┌───────────────────────────────────────────────────────────────────────┐
 │                        JETSON ORIN NANO (JetPack 6.2)                │
 │                                                                       │
 │   ┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐  │
 │   │   vslam-core     │     │   flight-bridge   │     │  Pixhawk 6C  │  │
 │   │   Container      │────▶│   Container       │────▶│  Mini (PX4)  │  │
 │   │                  │     │                   │     │              │  │
 │   │ • RealSense Node │     │ • MAVROS          │     │ • EKF2 VIO   │  │
 │   │ • cuVSLAM        │     │ • Pose Relay      │     │ • Position   │  │
 │   │ • IMU Fusion     │     │ • Flight Patterns │     │   Hold Mode  │  │
 │   └────────┬─────────┘     └─────────┬─────────┘     └──────────────┘  │
 │            │ IR Stereo + IMU          │ MAVLink UART                    │
 │            │ @90Hz / @200Hz           │ /dev/ttyUSB0                    │
 │   ┌────────▼─────────┐               │ @921600 baud                    │
 │   │  Intel RealSense  │               │                                │
 │   │  D435i (USB 3.0)  │               │                                │
 │   └──────────────────┘               │                                │
 └───────────────────────────────────────────────────────────────────────┘
```

## Hardware

| Component | Model | Interface |
|-----------|-------|-----------|
| Companion Computer | NVIDIA Jetson Orin Nano 8GB | — |
| Stereo + IMU Camera | Intel RealSense D435i | USB 3.0 |
| Flight Controller | Pixhawk 6C Mini | UART via FTDI |
| Autopilot Firmware | PX4 v1.15.4 | — |

## Software Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| OS | Ubuntu 22.04 (L4T) | JetPack 6.2 |
| Middleware | ROS 2 Humble | — |
| Visual SLAM | NVIDIA Isaac ROS cuVSLAM | 3.2 |
| MAV Bridge | MAVROS | Latest |
| Camera SDK | Intel RealSense | v2.55.1 / FW 5.13.0.50 |
| Containerization | Docker + NVIDIA Container Toolkit | 20.10+ |

## Project Layout

```
VSLAM-UAV/
│
├── containers/                   # Dockerized services
│   ├── vslam-core/               #   RealSense driver + camera node
│   ├── flight-bridge/            #   MAVROS + flight control
│   └── imu-calibration/          #   Allan variance analysis
│
├── launch/                       # ROS 2 launch files & configs
│   ├── vslam_realsense.launch.py #   VSLAM + RealSense pipeline
│   ├── flight_control.launch.py  #   MAVROS + pose relay
│   ├── vslam_realsense.rviz      #   RViz visualization config
│   └── config/
│       └── imu_params.yaml       #   IMU noise parameters
│
├── scripts/                      # Setup & utility scripts
│   ├── setup_vslam.sh            #   Install & launch cuVSLAM
│   ├── calibrate_imu.sh          #   Allan variance calibration
│   └── download_assets.sh        #   Download NVIDIA model assets
│
├── tools/                        # Post-flight analysis
│   ├── extract_trajectory.py     #   Parse rosbag to CSV
│   └── evaluate_accuracy.py      #   Ground truth comparison
│
├── assets/                       # UAV model files
│   └── iris_vslam.usd
│
├── udev/                         # Host USB rules
│   └── 99-realsense.rules
│
├── .env                          # Runtime configuration
├── docker-compose.yml            # Orchestration
├── Makefile                      # Quick commands
├── deploy.sh                     # One-click Jetson setup
├── DEPLOYMENT.md                 # Full deployment guide
└── LICENSE
```

## Quick Start

```bash
git clone https://github.com/jenarohi/VSLAM-UAV.git
cd VSLAM-UAV

# One-command deploy on Jetson
make deploy

# Or step by step
make build          # Build all containers
make up             # Start VSLAM + MAVROS
make logs           # Stream container logs
make down           # Stop everything
```

## PX4 Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `EKF2_EV_CTRL` | `15` | Fuse vision position + velocity + yaw |
| `EKF2_HGT_REF` | `3` | Vision as primary altitude source |
| `EKF2_EV_DELAY` | `0` | Minimal vision latency |
| `EKF2_GPS_CTRL` | `0` | GPS completely disabled |
| `COM_ARM_WO_GPS` | `1` | Allow GPS-denied arming |

## License

MIT License — See [LICENSE](LICENSE) for details.
