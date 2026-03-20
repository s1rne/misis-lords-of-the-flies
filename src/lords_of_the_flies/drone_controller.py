"""Main drone controller node for ROS2."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, Vector3
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32, Int32
import math

from .utils import PIDController, quaternion_to_euler, clamp


class DroneController(Node):
    """
    Main ROS2 node for drone control.

    Handles attitude control, velocity commands, sensor fusion,
    and emergency procedures for autonomous drone operations.
    """

    def __init__(self):
        super().__init__('drone_controller')

        self.declare_parameter('drone_id', '0')
        self.declare_parameter('max_velocity', 5.0)
        self.declare_parameter('max_altitude', 100.0)

        self.drone_id = self.get_parameter('drone_id').value
        self.max_velocity = self.get_parameter('max_velocity').value
        self.max_altitude = self.get_parameter('max_altitude').value

        self.roll_pid = PIDController(kp=1.0, ki=0.1, kd=0.5)
        self.pitch_pid = PIDController(kp=1.0, ki=0.1, kd=0.5)
        self.yaw_pid = PIDController(kp=2.0, ki=0.05, kd=0.3)

        self.current_altitude = 0.0
        self.current_velocity = [0.0, 0.0, 0.0]
        self.is_armed = False
        self.battery_level = 100.0

        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )

        self.motor_cmd_pub = self.create_publisher(Vector3, '/motor_commands', 10)
        self.status_pub = self.create_publisher(Int32, '/drone_status', 10)
        self.battery_pub = self.create_publisher(Float32, '/battery_level', 10)

        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info(f'DroneController initialized for drone {self.drone_id}')

    def cmd_vel_callback(self, msg: Twist):
        """Handle velocity commands from planner."""
        self.current_velocity = [
            clamp(msg.linear.x, -self.max_velocity, self.max_velocity),
            clamp(msg.linear.y, -self.max_velocity, self.max_velocity),
            clamp(msg.linear.z, -self.max_velocity, self.max_velocity),
        ]

    def imu_callback(self, msg: Imu):
        """Process IMU data for attitude estimation."""
        quat = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
        roll, pitch, yaw = quaternion_to_euler(quat)
        self.get_logger().debug(f'Attitude: R={roll:.2f}, P={pitch:.2f}, Y={yaw:.2f}')

    def control_loop(self):
        """Main control loop at 50 Hz."""
        if not self.is_armed:
            return

        motor_cmd = Vector3()
        motor_cmd.x = self.current_velocity[0]
        motor_cmd.y = self.current_velocity[1]
        motor_cmd.z = self.current_velocity[2]

        self.motor_cmd_pub.publish(motor_cmd)

        self.battery_level = max(0.0, self.battery_level - 0.05)
        battery_msg = Float32(data=self.battery_level)
        self.battery_pub.publish(battery_msg)

        if self.battery_level < 20.0:
            self.get_logger().warn(f'Low battery: {self.battery_level:.1f}%')

    def arm(self):
        """Arm the drone motors."""
        self.is_armed = True
        self.get_logger().info('Drone armed')

    def disarm(self):
        """Disarm the drone motors."""
        self.is_armed = False
        self.current_velocity = [0.0, 0.0, 0.0]
        self.get_logger().info('Drone disarmed')


def main(args=None):
    rclpy.init(args=args)
    controller = DroneController()
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.disarm()
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
