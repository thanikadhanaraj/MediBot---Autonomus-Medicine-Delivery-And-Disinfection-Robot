#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import Int32
import math
import time

class SmoothTranslateWaypointFollower(Node):
    def _init_(self):
        super()._init_('grid_move_controller')

        # ---------------- PATH ----------------
        self.waypoints = [
            (-0.33, -0.26),  # wp0
            (-0.33, 0.12),   # wp1 (SERVO)
            (0.33, 0.12),    # wp2 (DISINFECT)
            (0.33, -0.22)    # wp3
        ]
        self.loop_path = False

        # ---------------- SETTINGS ----------------
        self.deadzone = 0.02
        self.max_speed = 0.25
        self.kp = 1.2
        self.filter_alpha = 0.40
        self.dwell_secs = 0.5

        # Servo + disinfect settings
        self.servo_wp = 1
        self.servo_wait = 5
        self.servo_done = False

        self.disinfect_wp = 2
        self.disinfect_wait = 10
        self.disinfect_done = False

        # ---------------- INTERNAL STATE ----------------
        self.current_idx = 0
        self._arrived_time = None
        self.smoothed_x = None
        self.smoothed_y = None

        # ---------------- ROS PUB/SUB ----------------
        # subscribe to aruco pose
        self.pose_sub = self.create_subscription(
            PoseStamped, '/aruco_pose', self.pose_callback, 10)

        # send velocity commands to robot (ESP32 board A)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # send servo trigger to master board (ESP32 board B)
        self.servo_pub = self.create_publisher(Int32, '/servo_trigger', 10)

        # send disinfect timer to master board (ESP32 board B -> TM1637)
        self.display_pub = self.create_publisher(Int32, '/display_number', 10)

        self.get_logger().info("Robot navigation started.")
        self.print_path()

    def print_path(self):
        self.get_logger().info(f"Path length: {len(self.waypoints)} waypoints")
        for i, (x, y) in enumerate(self.waypoints):
            self.get_logger().info(f"  WP{i}: x={x:.3f}, y={y:.3f}")

    def stop_robot(self):
        # publish explicit zero floats to avoid C-level conversion issues
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.linear.y = 0.0
        cmd.angular.z = 0.0
        try:
            self.cmd_pub.publish(cmd)
        except Exception as e:
            self.get_logger().error(f"Failed to publish stop cmd: {e}")

    def _publish_servo(self):
        if self.servo_done:
            return
        msg = Int32()
        msg.data = 1
        try:
            self.servo_pub.publish(msg)
            self.get_logger().info("🟠 /servo_trigger published (servo start)")
        except Exception as e:
            self.get_logger().error(f"Failed to publish /servo_trigger: {e}")
        self.servo_done = True

    def _publish_disinfect_timer(self):
        if self.disinfect_done:
            return
        msg = Int32()
        msg.data = int(self.disinfect_wait)
        try:
            self.display_pub.publish(msg)
            self.get_logger().info(f"🟣 /display_number published ({msg.data})")
        except Exception as e:
            self.get_logger().error(f"Failed to publish /display_number: {e}")
        self.disinfect_done = True

    def pose_callback(self, msg: PoseStamped):
        # finished?
        if self.current_idx >= len(self.waypoints):
            self.stop_robot()
            return

        # read raw pos
        raw_x = msg.pose.position.x
        raw_y = msg.pose.position.y

        # smoothing init
        if self.smoothed_x is None:
            self.smoothed_x = raw_x
            self.smoothed_y = raw_y

        a = self.filter_alpha
        self.smoothed_x = a * self.smoothed_x + (1.0 - a) * raw_x
        self.smoothed_y = a * self.smoothed_y + (1.0 - a) * raw_y

        x = float(self.smoothed_x)
        y = float(self.smoothed_y)

        wp_x, wp_y = self.waypoints[self.current_idx]
        dx = float(wp_x - x)
        dy = float(wp_y - y)
        dist = math.hypot(dx, dy)

        # ARRIVED
        if dist <= self.deadzone:
            # ensure robot stopped
            self.stop_robot()

            if self._arrived_time is None:
                # first arrival at this waypoint -> record time and trigger events
                self._arrived_time = time.time()
                self.get_logger().info(f"ARRIVED at WP{self.current_idx}")

                if self.current_idx == self.servo_wp:
                    # trigger servo
                    self._publish_servo()

                if self.current_idx == self.disinfect_wp:
                    # trigger disinfect timer/LED
                    self._publish_disinfect_timer()

                return

            # still dwelling: check how long we have waited
            waited = time.time() - self._arrived_time

            # if at servo WP, wait servo_wait seconds before moving on
            if self.current_idx == self.servo_wp:
                remaining = self.servo_wait - waited
                if remaining > 0:
                    self.get_logger().info(f"🟠 Waiting for servo: {int(remaining)}s left")
                    return

            # if at disinfect WP, wait disinfect_wait seconds before moving on
            if self.current_idx == self.disinfect_wp:
                remaining = self.disinfect_wait - waited
                if remaining > 0:
                    self.get_logger().info(f"🟣 DISINFECT → {int(remaining)}s left")
                    return

            # done waiting -> move to next waypoint
            self._arrived_time = None
            self.current_idx += 1
            self.get_logger().info(f"➡ Advancing to WP{self.current_idx}")
            return

        # NORMAL MOVEMENT - proportional control
        vx = float(self.kp * dx)
        vy = float(self.kp * dy)

        mag = math.hypot(vx, vy)
        if mag > self.max_speed and mag > 1e-9:
            scale = float(self.max_speed / mag)
            vx *= scale
            vy *= scale

        # small deadband to avoid jitter
        if abs(vx) < 0.01:
            vx = 0.0
        if abs(vy) < 0.01:
            vy = 0.0

        # publish Twist with explicit floats
        cmd = Twist()
        cmd.linear.x = float(vx)
        cmd.linear.y = float(vy)
        cmd.angular.z = 0.0

        try:
            self.cmd_pub.publish(cmd)
        except Exception as e:
            self.get_logger().error(f"Failed to publish /cmd_vel: {e}")

        self.get_logger().info(
            f'wp={self.current_idx} target=({wp_x:.3f},{wp_y:.3f}) pos=({x:.3f},{y:.3f}) dx={dx:.3f} dy={dy:.3f} → MOVE'
        )


def main(args=None):
    rclpy.init(args=args)
    node = SmoothTranslateWaypointFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if _name_ == "_main_":
    main()