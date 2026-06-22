# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""
ROS 2 Launch file for Isaac ROS Visual SLAM with Intel RealSense D435i.
Configures stereo infrared streams and IMU for visual-inertial odometry.
"""

import os
import yaml
import launch
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


def load_imu_config():
    """Load IMU noise parameters from external YAML config."""
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'config', 'imu_params.yaml'
    )
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def generate_launch_description():
    """Configure and launch the VSLAM + RealSense pipeline."""

    imu_cfg = load_imu_config()

    # Default IMU noise values (overridden by config/imu_params.yaml if present)
    gyro_nd = 0.000244
    gyro_rw = 0.000019393
    accel_nd = 0.001862
    accel_rw = 0.003
    cal_freq = 200.0
    jitter_ms = 22.00

    if imu_cfg:
        gyro_nd = imu_cfg['imu_noise']['gyroscope']['noise_density']
        gyro_rw = imu_cfg['imu_noise']['gyroscope']['random_walk']
        accel_nd = imu_cfg['imu_noise']['accelerometer']['noise_density']
        accel_rw = imu_cfg['imu_noise']['accelerometer']['random_walk']
        cal_freq = imu_cfg['calibration']['frequency_hz']
        jitter_ms = imu_cfg['calibration']['image_jitter_threshold_ms']

    # ── RealSense D435i Camera Node ─────────────────────────────────────
    camera_node = Node(
        name='camera',
        namespace='camera',
        package='realsense2_camera',
        executable='realsense2_camera_node',
        parameters=[{
            'enable_infra1': True,
            'enable_infra2': True,
            'enable_color': False,
            'enable_depth': False,
            'depth_module.emitter_enabled': 0,
            'depth_module.profile': '640x360x90',
            'enable_gyro': True,
            'enable_accel': True,
            'gyro_fps': 200,
            'accel_fps': 200,
            'unite_imu_method': 2,
        }],
    )

    # ── Isaac ROS cuVSLAM Node ──────────────────────────────────────────
    vslam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising': False,
            'rectified_images': True,
            'enable_imu_fusion': True,
            'gyro_noise_density': gyro_nd,
            'gyro_random_walk': gyro_rw,
            'accel_noise_density': accel_nd,
            'accel_random_walk': accel_rw,
            'calibration_frequency': cal_freq,
            'image_jitter_threshold_ms': jitter_ms,
            'base_frame': 'camera_link',
            'imu_frame': 'camera_gyro_optical_frame',
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,
            'camera_optical_frames': [
                'camera_infra1_optical_frame',
                'camera_infra2_optical_frame',
            ],
        }],
        remappings=[
            ('visual_slam/image_0', 'camera/infra1/image_rect_raw'),
            ('visual_slam/camera_info_0', 'camera/infra1/camera_info'),
            ('visual_slam/image_1', 'camera/infra2/image_rect_raw'),
            ('visual_slam/camera_info_1', 'camera/infra2/camera_info'),
            ('visual_slam/imu', 'camera/imu'),
        ],
    )

    vslam_container = ComposableNodeContainer(
        name='visual_slam_launch_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[vslam_node],
        output='screen',
    )

    return launch.LaunchDescription([vslam_container, camera_node])
