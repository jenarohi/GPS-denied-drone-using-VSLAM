"""
Trajectory Accuracy Evaluation
Compares VSLAM estimated trajectory against ground truth (e.g., motion capture).
Computes ATE (Absolute Trajectory Error) and RPE (Relative Pose Error).
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path


def compute_ate(estimated: np.ndarray, ground_truth: np.ndarray) -> dict:
    """Compute Absolute Trajectory Error between two Nx3 position arrays."""
    errors = np.linalg.norm(estimated - ground_truth, axis=1)
    return {
        'ate_rmse': float(np.sqrt(np.mean(errors ** 2))),
        'ate_mean': float(np.mean(errors)),
        'ate_median': float(np.median(errors)),
        'ate_max': float(np.max(errors)),
        'ate_std': float(np.std(errors)),
        'num_samples': len(errors),
    }


def compute_rpe(estimated: np.ndarray, ground_truth: np.ndarray, delta: int = 1) -> dict:
    """Compute Relative Pose Error over fixed intervals."""
    est_deltas = estimated[delta:] - estimated[:-delta]
    gt_deltas = ground_truth[delta:] - ground_truth[:-delta]
    errors = np.linalg.norm(est_deltas - gt_deltas, axis=1)
    return {
        'rpe_rmse': float(np.sqrt(np.mean(errors ** 2))),
        'rpe_mean': float(np.mean(errors)),
        'rpe_max': float(np.max(errors)),
        'delta_frames': delta,
    }


def align_trajectories(est_df: pd.DataFrame, gt_df: pd.DataFrame) -> tuple:
    """Time-align estimated and ground truth trajectories via nearest timestamp."""
    aligned_est = []
    aligned_gt = []

    gt_times = gt_df['timestamp_ns'].values

    for _, row in est_df.iterrows():
        idx = np.argmin(np.abs(gt_times - row['timestamp_ns']))
        time_diff_ms = abs(gt_times[idx] - row['timestamp_ns']) / 1e6

        if time_diff_ms < 50:  # 50ms max alignment tolerance
            aligned_est.append([row['x'], row['y'], row['z']])
            gt_row = gt_df.iloc[idx]
            aligned_gt.append([gt_row['x'], gt_row['y'], gt_row['z']])

    return np.array(aligned_est), np.array(aligned_gt)


def main():
    parser = argparse.ArgumentParser(description='Evaluate VSLAM trajectory accuracy')
    parser.add_argument('estimated', help='CSV with estimated trajectory')
    parser.add_argument('ground_truth', help='CSV with ground truth trajectory')
    parser.add_argument('--rpe-delta', type=int, default=10, help='RPE frame interval')
    args = parser.parse_args()

    est_df = pd.read_csv(args.estimated)
    gt_df = pd.read_csv(args.ground_truth)

    print(f"▸ Estimated: {len(est_df)} samples")
    print(f"▸ Ground truth: {len(gt_df)} samples")

    est_pos, gt_pos = align_trajectories(est_df, gt_df)
    print(f"▸ Aligned: {len(est_pos)} matched pairs")

    if len(est_pos) < 10:
        print("✗ Too few aligned samples for evaluation")
        return

    ate = compute_ate(est_pos, gt_pos)
    rpe = compute_rpe(est_pos, gt_pos, delta=args.rpe_delta)

    print("\n── Absolute Trajectory Error (ATE) ──")
    print(f"  RMSE:   {ate['ate_rmse']:.4f} m")
    print(f"  Mean:   {ate['ate_mean']:.4f} m")
    print(f"  Median: {ate['ate_median']:.4f} m")
    print(f"  Max:    {ate['ate_max']:.4f} m")
    print(f"  Std:    {ate['ate_std']:.4f} m")

    print(f"\n── Relative Pose Error (RPE, Δ={args.rpe_delta}) ──")
    print(f"  RMSE:   {rpe['rpe_rmse']:.4f} m")
    print(f"  Mean:   {rpe['rpe_mean']:.4f} m")
    print(f"  Max:    {rpe['rpe_max']:.4f} m")


if __name__ == '__main__':
    main()
