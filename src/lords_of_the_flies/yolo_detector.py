"""YOLO-based object detection for maze objects."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import cv2
import numpy as np
from cv_bridge import CvBridge


class YOLODetector(Node):
    """
    Detect maze objects using YOLO.
    
    Classes:
    0 - Orange (апельсин)
    1 - Cheburashka (чебурашка)
    2 - Cheburashka with orange (чебурашка с апельсином)
    """

    def __init__(self):
        super().__init__('yolo_detector')
        
        self.declare_parameter('model_path', './config/yolo_weights.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('inference_size', 416)
        
        self.cv_bridge = CvBridge()
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.inference_size = self.get_parameter('inference_size').value
        
        # YOLO simulation (in real code would use actual YOLO library)
        self.detections = []
        self.object_counts = {'orange': 0, 'cheburashka': 0, 'cheburashka_orange': 0}
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.detect_callback, 10
        )
        
        # Publishers
        self.detections_pub = self.create_publisher(String, '/yolo/detections', 10)
        
        self.get_logger().info('YOLO Detector initialized')

    def detect_callback(self, msg: Image):
        """Process frame and detect objects."""
        try:
            frame = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Resize for inference
            resized = cv2.resize(frame, (self.inference_size, self.inference_size))
            
            # Simple mock detection based on color
            detections = self._mock_yolo_inference(resized)
            
            # Publish detections
            if detections:
                detection_str = self._format_detections(detections)
                msg = String()
                msg.data = detection_str
                self.detections_pub.publish(msg)
                
                self.detections = detections
                
        except Exception as e:
            self.get_logger().error(f'Detection error: {e}')

    def _mock_yolo_inference(self, frame):
        """
        Mock YOLO inference.
        Real implementation would use actual YOLO model.
        """
        detections = []
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Orange detection (brown/orange color)
        orange_lower = np.array([10, 100, 100])
        orange_upper = np.array([25, 255, 255])
        orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
        
        # Cheburashka detection (brown color)
        brown_lower = np.array([5, 50, 50])
        brown_upper = np.array([30, 200, 200])
        brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
        
        # Find contours
        orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        brown_contours, _ = cv2.findContours(brown_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process orange detections
        for contour in orange_contours:
            area = cv2.contourArea(contour)
            if 100 < area < 20000:
                x, y, w, h = cv2.boundingRect(contour)
                detections.append({
                    'class': 0,
                    'class_name': 'orange',
                    'confidence': 0.75,
                    'bbox': (x, y, w, h),
                    'center': (x + w//2, y + h//2)
                })
                self.object_counts['orange'] += 1
        
        # Process brown detections
        for contour in brown_contours:
            area = cv2.contourArea(contour)
            if 500 < area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                # Differentiate between cheburashka and cheburashka_with_orange
                if w > 50 or h > 50:
                    class_id = 2  # with orange
                    class_name = 'cheburashka_orange'
                else:
                    class_id = 1
                    class_name = 'cheburashka'
                
                detections.append({
                    'class': class_id,
                    'class_name': class_name,
                    'confidence': 0.70,
                    'bbox': (x, y, w, h),
                    'center': (x + w//2, y + h//2)
                })
                self.object_counts[class_name] += 1
        
        return detections

    def _format_detections(self, detections):
        """Format detections as readable string."""
        lines = [f"Detected {len(detections)} objects:"]
        for det in detections:
            lines.append(f"  - {det['class_name']}: confidence={det['confidence']:.2f}")
        return '\n'.join(lines)


def main(args=None):
    rclpy.init(args=args)
    detector = YOLODetector()
    try:
        rclpy.spin(detector)
    except KeyboardInterrupt:
        pass
    finally:
        detector.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
