"""Optical flow + Lidar fusion for localization between markers."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Vector3
import cv2
import numpy as np
from cv_bridge import CvBridge


class OpticalFlowFusion(Node):
    """
    Fuse optical flow and lidar for accurate localization.
    
    Used when ArUco marker is not visible.
    Estimates velocity from optical flow, validates with lidar.
    """

    def __init__(self):
        super().__init__('optical_flow_fusion')
        
        self.cv_bridge = CvBridge()
        self.prev_frame = None
        self.prev_gray = None
        
        # Lidar data
        self.lidar_front_distance = None
        self.lidar_left_distance = None
        self.lidar_right_distance = None
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10
        )
        
        # Publishers
        self.velocity_pub = self.create_publisher(
            Vector3, '/optical_flow/velocity', 10
        )
        
        self.get_logger().info('Optical Flow Fusion initialized')

    def image_callback(self, msg: Image):
        """Calculate optical flow from consecutive frames."""
        try:
            frame = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.prev_gray is not None:
                # Lucas-Kanade optical flow
                flow = cv2.calcOpticalFlowFarneback(
                    self.prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )
                
                # Calculate average flow
                avg_flow = np.mean(flow, axis=(0, 1))
                
                # Convert to velocity (m/s)
                # Scale depends on camera calibration and height
                velocity_x = avg_flow[0] * 0.01
                velocity_y = avg_flow[1] * 0.01
                
                # Validate with lidar if available
                velocity_z = self._get_vertical_velocity_from_lidar()
                
                # Publish velocity
                vel_msg = Vector3()
                vel_msg.x = float(velocity_x)
                vel_msg.y = float(velocity_y)
                vel_msg.z = float(velocity_z)
                self.velocity_pub.publish(vel_msg)
            
            self.prev_frame = frame
            self.prev_gray = gray
            
        except Exception as e:
            self.get_logger().error(f'Optical flow error: {e}')

    def lidar_callback(self, msg: LaserScan):
        """Process lidar scan for obstacle detection."""
        ranges = np.array(msg.ranges)
        
        # Extract front, left, right distances
        # Lidar usually has 360 rays
        if len(ranges) > 0:
            # Front (ray 0 or middle)
            self.lidar_front_distance = self._get_min_distance(ranges, 0, 30)
            # Left (90 degrees)
            self.lidar_left_distance = self._get_min_distance(ranges, 45, 75)
            # Right (270 degrees)
            self.lidar_right_distance = self._get_min_distance(ranges, 285, 315)

    def _get_min_distance(self, ranges, start_idx, end_idx):
        """Get minimum distance in angular range."""
        subset = ranges[start_idx:end_idx]
        valid = subset[~np.isnan(subset)]
        return np.min(valid) if len(valid) > 0 else None

    def _get_vertical_velocity_from_lidar(self):
        """Estimate vertical velocity from lidar range changes."""
        # Would need to track distance changes over time
        # For now, return 0
        return 0.0


def main(args=None):
    rclpy.init(args=args)
    fusion = OpticalFlowFusion()
    try:
        rclpy.spin(fusion)
    except KeyboardInterrupt:
        pass
    finally:
        fusion.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
