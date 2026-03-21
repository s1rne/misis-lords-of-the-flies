#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    drone_id_arg = DeclareLaunchArgument(
        'drone_id',
        default_value='0',
        description='Drone ID'
    )

    drone_controller = Node(
        package='lords_of_the_flies',
        executable='drone_controller',
        name='drone_controller',
        parameters=[
            {'drone_id': LaunchConfiguration('drone_id')},
            {'max_velocity': 5.0},
            {'max_altitude': 100.0},
        ],
        output='screen'
    )

    path_planner = Node(
        package='lords_of_the_flies',
        executable='path_planner',
        name='path_planner',
        parameters=[
            {'planning_rate': 10.0},
            {'collision_radius': 0.5},
        ],
        output='screen'
    )

    vision_processor = Node(
        package='lords_of_the_flies',
        executable='vision_processor',
        name='vision_processor',
        parameters=[
            {'enable_aruco': True},
            {'enable_slam': True},
        ],
        output='screen'
    )

    return LaunchDescription([
        drone_id_arg,
        drone_controller,
        path_planner,
        vision_processor,
    ])
