"""Unit tests for utility functions."""

import pytest
import math
import numpy as np
from lords_of_the_flies.utils import (
    distance_3d,
    normalize_vector,
    quaternion_to_euler,
    clamp,
    PIDController,
)


class TestDistance3D:
    def test_distance_same_point(self):
        assert distance_3d((0, 0, 0), (0, 0, 0)) == 0.0

    def test_distance_unit_vector(self):
        assert distance_3d((0, 0, 0), (1, 0, 0)) == 1.0
        assert distance_3d((0, 0, 0), (0, 1, 0)) == 1.0
        assert distance_3d((0, 0, 0), (0, 0, 1)) == 1.0

    def test_distance_3d_calculation(self):
        result = distance_3d((0, 0, 0), (3, 4, 0))
        assert result == 5.0


class TestNormalizeVector:
    def test_normalize_unit_vector(self):
        v = np.array([1.0, 0.0, 0.0])
        normalized = normalize_vector(v)
        assert np.allclose(normalized, v)

    def test_normalize_arbitrary_vector(self):
        v = np.array([3.0, 4.0, 0.0])
        normalized = normalize_vector(v)
        assert np.allclose(np.linalg.norm(normalized), 1.0)


class TestClamp:
    def test_clamp_within_bounds(self):
        assert clamp(5.0, 0, 10) == 5.0

    def test_clamp_below_min(self):
        assert clamp(-5.0, 0, 10) == 0.0

    def test_clamp_above_max(self):
        assert clamp(15.0, 0, 10) == 10.0


class TestPIDController:
    def test_pid_initialization(self):
        pid = PIDController(1.0, 0.1, 0.5)
        assert pid.kp == 1.0
        assert pid.ki == 0.1
        assert pid.kd == 0.5

    def test_pid_proportional(self):
        pid = PIDController(1.0, 0.0, 0.0)
        output = pid.update(1.0, 0.1)
        assert output == 1.0

    def test_pid_reset(self):
        pid = PIDController(1.0, 0.1, 0.5)
        pid.update(1.0, 0.1)
        pid.reset()
        assert pid.prev_error == 0
        assert pid.integral == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
