"""
Lords of the Flies - Autonomous Drone Swarm Control System for ROS2

A cutting-edge solution for coordinated multi-drone operations,
featuring autonomous path planning, vision-based navigation,
and real-time swarm coordination.
"""

__version__ = '0.1.0'
__author__ = 'Alexander Simaranov'

from . import drone_controller
from . import swarm_coordinator
from . import path_planner
from . import vision_processor
from . import utils

__all__ = [
    'drone_controller',
    'swarm_coordinator',
    'path_planner',
    'vision_processor',
    'utils',
]
