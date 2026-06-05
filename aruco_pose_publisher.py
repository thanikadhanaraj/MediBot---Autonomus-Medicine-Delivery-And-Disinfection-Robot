#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import cv2
import numpy as np
import math
import os

class ArucoPosePublisher(Node):
    def _init_(self):
        super()._init_('aruco_pose_publisher')

        self.pose_pub = self.create_publisher(PoseStamped, '/aruco_pose', 10)

        # --- camera and ArUco parameters ---
        self.cap = cv2.VideoCapture(0)  # change to 1 if second camera
        self.marker_length = 0.05       # marker side (in meters)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
        self.parameters = cv2.aruco.DetectorParameters_create()

        # --- load calibration ---
        pkg_dir = os.path.dirname(_file_)
        cam_path = os.path.join(pkg_dir, 'camera_matrix.npy')
        dist_path = os.path.join(pkg_dir, 'dist_coeffs.npy')

        if os.path.exists(cam_path) and os.path.exists(dist_path):
            self.camera_matrix = np.load(cam_path)
            self.dist_coeffs = np.load(dist_path)
        else:
            self.get_logger().warn("⚠ Camera calibration files not found, using default values")
            self.camera_matrix = np.array([[800, 0, 320],
                                           [0, 800, 240],
                                           [0,   0,   1]], dtype=float)
            self.dist_coeffs = np.zeros((5, 1), dtype=float)

        self.timer = self.create_timer(0.1, self.detect_and_publish)
        self.get_logger().info("✅ ArUco Pose Publisher started")

    def detect_and_publish(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Camera frame not available")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_length, self.camera_matrix, self.dist_coeffs)

            tvec = tvecs[0][0]
            rvec = rvecs[0][0]
            R, _ = cv2.Rodrigues(rvec)
            yaw = math.atan2(R[1, 0], R[0, 0])

            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.pose.position.x = float(tvec[0])
            msg.pose.position.y = float(tvec[1])
            msg.pose.position.z = float(tvec[2])
            msg.pose.orientation.z = float(yaw)

            self.pose_pub.publish(msg)
            self.get_logger().info(f"x={tvec[0]:.2f}m, y={tvec[1]:.2f}m, yaw={math.degrees(yaw):.1f}°")

            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.03)

        cv2.imshow("Aruco Detection", frame)
        cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = ArucoPosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if _name_ == '_main_':
    main()