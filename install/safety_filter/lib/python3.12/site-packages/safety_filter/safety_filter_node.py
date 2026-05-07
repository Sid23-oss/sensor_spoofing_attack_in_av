#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class SafetyFilterNode(Node):
    def __init__(self):
        super().__init__('safety_filter_node')

        # Limits
        self.max_linear_x = 1.0
        self.max_angular_z = 1.0

        # Emergency stop if robot seems too fast from odometry
        self.max_measured_speed = 1.2

        self.latest_speed = 0.0
        self.estop = False

        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Read raw commands from a safe testing topic
        self.raw_sub = self.create_subscription(
            Twist,
            '/raw_cmd_vel',
            self.raw_cmd_callback,
            10
        )

        # Read robot feedback
        self.odom_sub = self.create_subscription(
            Odometry,
            '/model/vehicle_blue/odometry',
            self.odom_callback,
            10
        )

        # Publish approved commands to the real robot topic
        self.safe_pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            reliable_qos
        )

        self.get_logger().info('Safety filter started.')
        self.get_logger().info('Input:  /raw_cmd_vel')
        self.get_logger().info('Output: /model/vehicle_blue/cmd_vel')

    def odom_callback(self, msg: Odometry):
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        self.latest_speed = math.sqrt(vx * vx + vy * vy)

        if self.latest_speed > self.max_measured_speed:
            self.estop = True
            self.get_logger().warn(
                f'E-STOP triggered: measured speed {self.latest_speed:.2f} m/s'
            )

    def raw_cmd_callback(self, msg: Twist):
        safe_cmd = Twist()

        if self.estop:
            self.safe_pub.publish(safe_cmd)
            self.get_logger().warn('Blocked command: E-STOP is active')
            return

        # Clamp linear x
        safe_cmd.linear.x = max(
            -self.max_linear_x,
            min(self.max_linear_x, msg.linear.x)
        )

        # Clamp angular z
        safe_cmd.angular.z = max(
            -self.max_angular_z,
            min(self.max_angular_z, msg.angular.z)
        )

        if safe_cmd.linear.x != msg.linear.x or safe_cmd.angular.z != msg.angular.z:
            self.get_logger().warn(
                f'Command clamped | '
                f'in: lin={msg.linear.x:.2f}, ang={msg.angular.z:.2f} | '
                f'out: lin={safe_cmd.linear.x:.2f}, ang={safe_cmd.angular.z:.2f}'
            )

        self.safe_pub.publish(safe_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SafetyFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rcply.ok():
                rcply.shutdown()
        




if __name__ == '__main__':
    main()

