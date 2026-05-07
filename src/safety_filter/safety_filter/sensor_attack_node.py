#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range

import sys
import select
import termios
import tty


class SensorAttackNode(Node):

    def __init__(self):
        super().__init__('sensor_attack_node')

        self.front_pub = self.create_publisher(Range, '/ultrasonic_attack/front', 10)
        self.left_pub = self.create_publisher(Range, '/ultrasonic_attack/left', 10)
        self.right_pub = self.create_publisher(Range, '/ultrasonic_attack/right', 10)
        self.rear_pub = self.create_publisher(Range, '/ultrasonic_attack/rear', 10)

        self.settings = termios.tcgetattr(sys.stdin)

        self.attack_mode = "stop"

        # Keep publishing fake sensor data continuously
        self.timer = self.create_timer(0.05, self.publish_attack)

        self.get_logger().info('STRONG sensor attack node started')
        self.get_logger().info('Use arrows: ↑ forward, ↓ reverse, ← left, → right, SPACE stop, q quit')

    def make_msg(self, value):
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.5
        msg.min_range = 0.02
        msg.max_range = 4.0
        msg.range = value
        return msg

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)

        key = ''
        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish_all(self, front, left, right, rear):
        self.front_pub.publish(self.make_msg(front))
        self.left_pub.publish(self.make_msg(left))
        self.right_pub.publish(self.make_msg(right))
        self.rear_pub.publish(self.make_msg(rear))

    def publish_attack(self):

        if self.attack_mode == "forward":
            # Make front look clear, rear blocked
            self.publish_all(
                front=4.0,
                left=2.0,
                right=2.0,
                rear=0.2
            )

        elif self.attack_mode == "reverse":
            # Make front look blocked and rear clear
            self.publish_all(
                front=0.2,
                left=2.0,
                right=2.0,
                rear=4.0
            )

        elif self.attack_mode == "left":
            # Make left side look clear, right side blocked
            self.publish_all(
                front=0.4,
                left=4.0,
                right=0.2,
                rear=2.0
            )

        elif self.attack_mode == "right":
            # Make right side look clear, left side blocked
            self.publish_all(
                front=0.4,
                left=0.2,
                right=4.0,
                rear=2.0
            )

        elif self.attack_mode == "stop":
            # Make every direction look blocked
            self.publish_all(
                front=0.2,
                left=0.2,
                right=0.2,
                rear=0.2
            )

    def run(self):
        try:
            while rclpy.ok():
                key = self.get_key()

                if key == '\x1b[A':
                    self.attack_mode = "forward"
                    self.get_logger().info('ATTACK MODE: FORWARD')

                elif key == '\x1b[B':
                    self.attack_mode = "reverse"
                    self.get_logger().info('ATTACK MODE: REVERSE')

                elif key == '\x1b[D':
                    self.attack_mode = "left"
                    self.get_logger().info('ATTACK MODE: LEFT')

                elif key == '\x1b[C':
                    self.attack_mode = "right"
                    self.get_logger().info('ATTACK MODE: RIGHT')

                elif key == ' ':
                    self.attack_mode = "stop"
                    self.get_logger().info('ATTACK MODE: STOP')

                elif key == 'q':
                    break

                rclpy.spin_once(self, timeout_sec=0.01)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


def main(args=None):
    rclpy.init(args=args)
    node = SensorAttackNode()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
