"""
ROS 2 Launch file for MAVROS flight control bridge.
Connects cuVSLAM visual odometry to PX4 via MAVROS and launches flight patterns.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, TextSubstitution, EnvironmentVariable
from launch_ros.actions import Node
from launch.launch_description_sources import AnyLaunchDescriptionSource


def generate_launch_description():
    """Build the MAVROS + pose relay + flight pattern launch graph."""

    # ── Arguments ───────────────────────────────────────────────────────
    arg_fcu = DeclareLaunchArgument(
        'fcu_url',
        default_value=EnvironmentVariable('PIXHAWK_PORT', default_value='/dev/ttyUSB0:921600'),
        description='MAVLink connection string for Pixhawk'
    )

    arg_pattern = DeclareLaunchArgument(
        'pattern',
        default_value='square',
        description='Autonomous flight pattern (square, circle, etc.)'
    )

    # ── MAVROS (PX4 bridge) ─────────────────────────────────────────────
    px4_launch = os.path.expanduser(
        '~/ros2_ws/install/mavros/share/mavros/launch/px4.launch'
    )

    mavros_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(px4_launch),
        launch_arguments={'fcu_url': LaunchConfiguration('fcu_url')}.items()
    )

    # ── VIO Pose Relay ──────────────────────────────────────────────────
    # Bridges cuVSLAM output to MAVROS vision input
    pose_relay = Node(
        package='topic_tools',
        executable='relay',
        name='vio_pose_relay',
        output='screen',
        arguments=[
            '/visual_slam/tracking/vo_pose_covariance',
            '/mavros/vision_pose/pose_cov',
        ]
    )

    # ── Flight Pattern Controller ───────────────────────────────────────
    flight_executable = [
        LaunchConfiguration('pattern'),
        TextSubstitution(text='_py'),
    ]

    flight_node = Node(
        package='mavrospy',
        executable=flight_executable,
        name='flight_controller',
        output='screen',
        parameters=[{'vision': True}]
    )

    return LaunchDescription([
        arg_pattern,
        arg_fcu,
        mavros_launch,
        pose_relay,
        flight_node,
    ])
