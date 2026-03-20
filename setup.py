from setuptools import setup, find_packages
import os

setup(
    name='lords_of_the_flies',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'rclpy',
        'numpy',
        'opencv-python',
        'dronekit',
    ],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'drone_controller=lords_of_the_flies.drone_controller:main',
            'swarm_coordinator=lords_of_the_flies.swarm_coordinator:main',
            'path_planner=lords_of_the_flies.path_planner:main',
            'vision_processor=lords_of_the_flies.vision_processor:main',
        ],
    },
)
