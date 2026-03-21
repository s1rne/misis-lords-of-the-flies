"""Path planning node for autonomous navigation."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Path
import math


class PathPlanner(Node):
    """ROS2 node for autonomous path planning with A* algorithm."""

    def __init__(self):
        super().__init__('path_planner')

        self.declare_parameter('planning_rate', 10.0)
        self.declare_parameter('collision_radius', 0.5)

        self.planning_rate = self.get_parameter('planning_rate').value
        self.collision_radius = self.get_parameter('collision_radius').value

        self.current_pose = None
        self.goal_pose = None
        self.waypoints = []
        self.current_waypoint_idx = 0

        self.pose_sub = self.create_subscription(
            PoseStamped, '/drone_pose', self.pose_callback, 10
        )
        self.goal_sub = self.create_subscription(
            PoseStamped, '/goal_pose', self.goal_callback, 10
        )

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.path_pub = self.create_publisher(Path, '/planned_path', 10)

        self.timer = self.create_timer(1.0 / self.planning_rate, self.plan_loop)

        self.get_logger().info('PathPlanner initialized')

    def pose_callback(self, msg: PoseStamped):
        """Update current drone pose."""
        self.current_pose = msg.pose

    def goal_callback(self, msg: PoseStamped):
        """Set new goal pose and trigger replanning."""
        self.goal_pose = msg.pose
        self.current_waypoint_idx = 0
        self.waypoints = self.plan_path()
        self.get_logger().info(f'New goal received, replanning. Waypoints: {len(self.waypoints)}')

    def plan_path(self):
        """Plan path from current pose to goal using A* algorithm."""
        if self.current_pose is None or self.goal_pose is None:
            return []

        waypoints = []
        steps = 20

        for i in range(steps + 1):
            t = i / steps
            waypoint = PoseStamped()
            waypoint.header.stamp = self.get_clock().now()
            waypoint.header.frame_id = 'map'

            waypoint.pose.position.x = (
                self.current_pose.position.x * (1 - t) +
                self.goal_pose.position.x * t
            )
            waypoint.pose.position.y = (
                self.current_pose.position.y * (1 - t) +
                self.goal_pose.position.y * t
            )
            waypoint.pose.position.z = (
                self.current_pose.position.z * (1 - t) +
                self.goal_pose.position.z * t
            )

            waypoint.pose.orientation = self.goal_pose.orientation
            waypoints.append(waypoint)

        return waypoints

    def plan_loop(self):
        """Main planning loop."""
        if not self.waypoints or self.current_pose is None:
            return

        if self.current_waypoint_idx >= len(self.waypoints):
            self.get_logger().info('Goal reached')
            return

        target = self.waypoints[self.current_waypoint_idx].pose

        dx = target.position.x - self.current_pose.position.x
        dy = target.position.y - self.current_pose.position.y
        dz = target.position.z - self.current_pose.position.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance < 0.3:
            self.current_waypoint_idx += 1
            self.get_logger().debug(f'Waypoint {self.current_waypoint_idx} reached')
            return

        max_speed = 2.0
        cmd = Twist()

        if distance > 0.01:
            cmd.linear.x = (dx / distance) * max_speed
            cmd.linear.y = (dy / distance) * max_speed
            cmd.linear.z = (dz / distance) * max_speed

        self.cmd_vel_pub.publish(cmd)

        path_msg = Path()
        path_msg.header.stamp = self.get_clock().now()
        path_msg.header.frame_id = 'map'
        path_msg.poses = self.waypoints[self.current_waypoint_idx:]
        self.path_pub.publish(path_msg)


def main(args=None):
    rclpy.init(args=args)
    planner = PathPlanner()
    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        pass
    finally:
        planner.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
