#!/bin/bash
# Allan Variance IMU Calibration for RealSense D435i
# Records static IMU data and runs allan_ros2 analysis

set -e

ROSBAG_DIR="/home/analysis/imu_rosbag"
ALLAN_CONFIG=~/ros2_ws/src/allan_ros2/config/config.yaml

# Locate the recorded .db3 file
DB3_FILE=$(find "$ROSBAG_DIR" -maxdepth 1 -name "*.db3" -print -quit)

if [ -z "$DB3_FILE" ]; then
    echo "✗ No .db3 rosbag found in $ROSBAG_DIR"
    echo "  Record one first:  ros2 bag record /camera/imu -o $ROSBAG_DIR"
    exit 1
fi

echo "▸ Found rosbag: $DB3_FILE"

# Write allan_ros2 config
cat <<EOF > "$ALLAN_CONFIG"
allan_node:
  ros__parameters:
     topic: /camera/imu
     bag_path: $DB3_FILE
     msg_type: ros
     publish_rate: 200
     sample_rate: 200
EOF

echo "▸ Config written to $ALLAN_CONFIG"

# Build and source
cd ~/ros2_ws
echo "▸ Building allan_ros2..."
colcon build --packages-select allan_ros2 2>&1 | tail -3
source ~/ros2_ws/install/setup.bash

echo "▸ Ready. Run:  ros2 run allan_ros2 allan_node"
