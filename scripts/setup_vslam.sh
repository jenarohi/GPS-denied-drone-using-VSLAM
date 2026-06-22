#!/bin/bash
# Install and launch Isaac ROS Visual SLAM with RealSense support

set -e

echo "▸ Updating packages..."
sudo apt-get update -qq

echo "▸ Installing Isaac ROS Visual SLAM..."
sudo apt-get install -y -qq ros-humble-isaac-ros-visual-slam

echo "▸ Installing Isaac ROS RealSense integration..."
sudo apt-get install -y -qq ros-humble-isaac-ros-examples ros-humble-isaac-ros-realsense

export ROS_DOMAIN_ID=1

echo "▸ Launching cuVSLAM pipeline..."
ros2 launch vslam_realsense.launch.py
