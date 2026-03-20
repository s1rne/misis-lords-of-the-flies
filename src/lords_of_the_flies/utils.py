"""Utility functions for drone control system."""

import math
import numpy as np
from typing import Tuple


def distance_3d(p1: Tuple[float, float, float],
                p2: Tuple[float, float, float]) -> float:
    """Calculate 3D Euclidean distance between two points."""
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2 +
        (p1[2] - p2[2]) ** 2
    )


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normalize a vector to unit length."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def quaternion_to_euler(quat: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
    """Convert quaternion to Euler angles (roll, pitch, yaw)."""
    x, y, z, w = quat

    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    sinp = max(-1, min(1, sinp))
    pitch = math.asin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


class PIDController:
    """Simple PID controller for drone stabilization."""

    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update(self, error: float, dt: float) -> float:
        """Calculate PID output."""
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        output = (self.kp * error +
                  self.ki * self.integral +
                  self.kd * derivative)
        return output

    def reset(self):
        """Reset PID state."""
        self.prev_error = 0
        self.integral = 0
