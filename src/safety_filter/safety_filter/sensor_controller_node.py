#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Range
from geometry_msgs.msg import Twist


class SensorControllerNode(Node):

    def __init__(self):
        super().__init__('sensor_controller_node')

        # Default sensor values
        self.front = 4.0
        self.left = 4.0
        self.right = 4.0
        self.rear = 4.0

        # Subscribe to 4 ultrasonic sensors
        self.create_subscription(
            Range,
            '/ultrasonic/front',
            self.front_callback,
            10
        )

        self.create_subscription(
            Range,
            '/ultrasonic/left',
            self.left_callback,
            10
        )

        self.create_subscription(
            Range,
            '/ultrasonic/right',
            self.right_callback,
            10
        )

        self.create_subscription(
            Range,
            '/ultrasonic/rear',
            self.rear_callback,
            10
        )

        # IMPORTANT:
        # Directly publishing to Gazebo robot topic now
        # because we are NOT using old safety_filter_node
        self.cmd_pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        # Run control logic every 0.2 seconds
        self.timer = self.create_timer(
            0.2,
            self.control_loop
        )

        self.get_logger().info('Sensor controller node started')

    def front_callback(self, msg):
        self.front = msg.range

    def left_callback(self, msg):
        self.left = msg.range

    def right_callback(self, msg):
        self.right = msg.range

    def rear_callback(self, msg):
        self.rear = msg.range

    def control_loop(self):
        cmd = Twist()

        # Case 1: Obstacle very close in front
        if self.front < 0.8:
            cmd.linear.x = 0.0

            # Turn toward the side with more free space
            if self.left > self.right:
                cmd.angular.z = 0.8   # turn left
            else:
                cmd.angular.z = -0.8  # turn right

        # Case 2: Path is clear
        else:
            cmd.linear.x = 0.4

            # Slight steering based on side sensor difference
            difference = self.left - self.right

            if difference > 0.5:
                cmd.angular.z = 0.4   # turn left slowly
            elif difference < -0.5:
                cmd.angular.z = -0.4  # turn right slowly
            else:
                cmd.angular.z = 0.0   # go straight

        self.cmd_pub.publish(cmd)

        self.get_logger().info(
            f'Front={self.front:.2f} '
            f'Left={self.left:.2f} '
            f'Right={self.right:.2f} '
            f'Rear={self.rear:.2f} | '
            f'Linear={cmd.linear.x:.2f} '
            f'Angular={cmd.angular.z:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = SensorControllerNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
