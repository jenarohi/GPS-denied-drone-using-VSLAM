"""
Trajectory Extraction Tool
Parses ROS 2 bag files and exports VSLAM pose data to CSV for analysis.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr


def extract_poses(bag_path: str, topic: str) -> pd.DataFrame:
    """Read pose messages from a rosbag and return as DataFrame."""
    records = []

    with Reader(bag_path) as reader:
        target_connections = [c for c in reader.connections if c.topic == topic]

        if not target_connections:
            available = [c.topic for c in reader.connections]
            print(f"Topic '{topic}' not found. Available: {available}")
            sys.exit(1)

        for conn, timestamp, raw_data in reader.messages(connections=target_connections):
            msg = deserialize_cdr(raw_data, conn.msgtype)
            pose = msg.pose.pose

            records.append({
                'timestamp_ns': timestamp,
                'x': pose.position.x,
                'y': pose.position.y,
                'z': pose.position.z,
                'qx': pose.orientation.x,
                'qy': pose.orientation.y,
                'qz': pose.orientation.z,
                'qw': pose.orientation.w,
            })

    return pd.DataFrame(records)


def main():
    parser = argparse.ArgumentParser(description='Extract VSLAM trajectory from rosbag')
    parser.add_argument('bag_path', help='Path to ROS 2 bag directory')
    parser.add_argument('--topic', default='/visual_slam/tracking/vo_pose_covariance',
                        help='Pose topic name')
    parser.add_argument('--output', default='trajectory.csv', help='Output CSV path')
    args = parser.parse_args()

    print(f"▸ Reading bag: {args.bag_path}")
    df = extract_poses(args.bag_path, args.topic)
    df.to_csv(args.output, index=False)
    print(f"✓ Exported {len(df)} poses to {args.output}")


if __name__ == '__main__':
    main()
