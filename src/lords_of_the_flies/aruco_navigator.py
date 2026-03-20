"""ArUco marker-based localization and navigation."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped, PointStamped
from std_msgs.msg import Int32, Float32MultiArray
import cv2
import numpy as np
from cv_bridge import CvBridge


class ArUcoNavigator(Node):
    """
    Navigate maze using ArUco markers on floor.
    
    Each floor cell (0.8x0.8m) has ArUco marker.
    Camera points down, detects marker -> knows exact position.
    """

    def __init__(self):
        super().__init__('aruco_navigator')
        
        self.declare_parameter('marker_size', 0.8)  # meters
        self.declare_parameter('flight_height', 1.5)  # meters above floor
        self.declare_parameter('aruco_dict', 'DICT_5X5_100')
        
        self.marker_size = self.get_parameter('marker_size').value
        self.flight_height = self.get_parameter('flight_height').value
        
        self.cv_bridge = CvBridge()
        
        # Camera calibration (примерные значения, должны измерить)
        self.camera_matrix = np.array([
            [500, 0, 320],
            [0, 500, 240],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # ArUco setup
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict)
        
        # Current state
        self.current_marker_id = None
        self.current_position = None
        self.detected_markers = {}
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        
        # Publishers
        self.position_pub = self.create_publisher(
            PoseStamped, '/drone/current_position', 10
        )
        self.markers_pub = self.create_publisher(
            Float32MultiArray, '/aruco/detected_markers', 10
        )
        self.target_marker_pub = self.create_publisher(
            Int32, '/aruco/target_marker', 10
        )
        
        self.timer = self.create_timer(0.033, self.publish_position)  # 30Hz
        self.get_logger().info('ArUco Navigator initialized')

    def image_callback(self, msg: Image):
        """Detect ArUco markers and estimate position."""
        try:
            frame = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect markers
            corners, ids, rejected = self.detector.detectMarkers(gray)
            
            if ids is not None:
                # Process detections
                for i, marker_id in enumerate(ids.flatten()):
                    corner = corners[i][0]
                    
                    # Estimate pose of marker
                    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                        corner[np.newaxis, :, :],
                        self.marker_size,
                        self.camera_matrix,
                        np.zeros(4)
                    )
                    
                    # Store marker info
                    self.detected_markers[int(marker_id)] = {
                        'position': tvec[0, 0, :2].copy(),  # x, y in meters
                        'confidence': 1.0,
                        'tvec': tvec[0, 0, :],
                        'rvec': rvec[0, 0, :]
                    }
                    
                    # Set as current if most prominent
                    if self.current_marker_id is None:
                        self.current_marker_id = int(marker_id)
                        self.current_position = self.detected_markers[int(marker_id)]['position'].copy()
                    elif marker_id == self.current_marker_id:
                        self.current_position = self.detected_markers[int(marker_id)]['position'].copy()
                        
        except Exception as e:
            self.get_logger().error(f'ArUco detection error: {e}')

    def publish_position(self):
        """Publish current position based on detected markers."""
        if self.current_position is None:
            return
        
        # Publish position
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now()
        pose_msg.header.frame_id = 'map'
        pose_msg.pose.position.x = float(self.current_position[0])
        pose_msg.pose.position.y = float(self.current_position[1])
        pose_msg.pose.position.z = self.flight_height
        
        self.position_pub.publish(pose_msg)
        
        # Publish detected markers list
        markers_msg = Float32MultiArray()
        markers_data = []
        for marker_id, info in self.detected_markers.items():
            markers_data.extend([marker_id, info['position'][0], info['position'][1]])
        markers_msg.data = markers_data
        self.markers_pub.publish(markers_msg)


def main(args=None):
    rclpy.init(args=args)
    navigator = ArUcoNavigator()
    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
