# GPS-Denied Drone using VSLAM

> GPS-Denied Autonomous UAV Navigation using Visual SLAM & VIO

Dockerized pipeline for real-time Visual SLAM on NVIDIA Jetson Orin, enabling fully autonomous GPS-denied flight using stereo-inertial odometry from Intel RealSense D435i and NVIDIA Isaac ROS cuVSLAM.

---

## Hardware

| Component | Model | Interface |
|-----------|-------|-----------|
| Companion Computer | NVIDIA Jetson Orin Nano 8GB | — |
| Stereo + IMU Camera | Intel RealSense D435i | USB 3.0 |
| Flight Controller | Pixhawk 6C Mini | UART via FTDI |
| Autopilot Firmware | PX4 v1.15.4 | — |

---

## Software Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| OS | Ubuntu 22.04 (L4T) | JetPack 6.2 |
| Middleware | ROS 2 Humble | — |
| Visual SLAM | NVIDIA Isaac ROS cuVSLAM | 3.2 |
| MAV Bridge | MAVROS | Latest |
| Camera SDK | Intel RealSense | v2.55.1 / FW 5.13.0.50 |
| Containerization | Docker + NVIDIA Container Toolkit | 20.10+ |

---

## Project Layout
GPS-denied-drone-using-VSLAM/

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

│   ├── download_assets.sh        #   Download NVIDIA model assets

│   └── start_realsense.sh        #   Launch RealSense ROS node

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

└── LICENSE

---

## Prerequisites

- NVIDIA Jetson Orin Nano 8GB (JetPack 6.2)
- Intel RealSense D435i (USB 3.0)
- Pixhawk connected via USB-to-UART adapter on `/dev/ttyUSB0`
- Docker + NVIDIA Container Toolkit installed on Jetson

Confirm JetPack version:
```bash
cat /etc/nv_tegra_release
```
Output should show `R36` and `REVISION: 4.3`

Set CPU/GPU to max performance:
```bash
sudo /usr/bin/jetson_clocks
sudo /usr/sbin/nvpmodel -m 2
```

Add user to Docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## Deployment

### 1. Clone the repo
```bash
git clone https://github.com/jenarohi/GPS-denied-drone-using-VSLAM.git
cd GPS-denied-drone-using-VSLAM
```

### 2. Build all containers
This builds three containers — `vslam-core` (RealSense + ROS2), `flight-bridge` (MAVROS + PX4), and `imu-calibration` (Allan variance).
```bash
docker compose build
```
> First build takes 20–40 minutes. It compiles librealsense v2.55.1, RealSense ROS wrapper, and full MAVROS workspace from source.

### 3. Start the VSLAM pipeline
```bash
docker compose up -d vslam-core flight-bridge
```

### 4. Verify containers are running
```bash
docker compose ps
```
Both `vslam-core` and `flight-bridge` should show status `Up`.

### 5. Stream live logs
```bash
docker compose logs -f
```

### 6. Stop everything
```bash
docker compose down
```

---

## Container Access

Shell into the VSLAM container:
```bash
docker exec -it vslam-core bash
```

Shell into the MAVROS container:
```bash
docker exec -it flight-bridge bash
```

---

## IMU Calibration (One-time, Optional)

Run this once before first flight to characterize the D435i IMU using Allan Variance analysis.

Start the calibration container:
```bash
docker compose --profile calibration up -d imu-calibration
docker exec -it imu-calibration bash
```

Inside the container, record static IMU data for at least 3 hours:
```bash
ros2 bag record -o imu_rosbag /camera/imu
```

Stop with `CTRL+C`, then run Allan variance analysis:
```bash
ros2 launch allan_ros2 allan_node.py
python3 ~/ros2_ws/src/allan_ros2/scripts/analysis.py --data deviation.csv
```

Update the output values (`gyro_noise_density`, `gyro_random_walk`, `accel_noise_density`, `accel_random_walk`) in `launch/config/imu_params.yaml`.

---

## Other Commands

| Task | Command |
|------|---------|
| Force rebuild (no cache) | `docker compose build --no-cache` |
| Remove all containers + images | `docker compose down --rmi all --volumes` |
| Check Pixhawk connection | `ls /dev/ttyUSB0` |

---

## PX4 Parameters

Set these in QGroundControl before flight:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `MAV_1_CONFIG` | `TELEM2` | Route MAVLink to TELEM2 |
| `SER_TEL2_BAUD` | `921600` | Match UART baud rate |
| `EKF2_EV_CTRL` | `15` | Fuse vision position + velocity + yaw |
| `EKF2_HGT_REF` | `3` | Vision as primary altitude source |
| `EKF2_EV_DELAY` | `50` | Vision latency compensation |
| `EKF2_GPS_CTRL` | `0` | Disable GPS entirely |
| `COM_ARM_WO_GPS` | `1` | Allow arming without GPS |

---

## License

MIT License — See [LICENSE](LICENSE) for details.
