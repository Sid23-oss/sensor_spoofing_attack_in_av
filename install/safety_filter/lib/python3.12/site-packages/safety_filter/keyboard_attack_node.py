#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import sys
import select
import termios
import tty


class KeyboardAttackNode(Node):

    def __init__(self):
        super().__init__('keyboard_attack_node')

        self.publisher = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        self.linear_speed = 0.6
        self.angular_speed = 1.0

        self.get_logger().info('Keyboard attack node started')
        self.get_logger().info('Use arrow keys to control robot. Press q to quit.')

    def get_key(self):
        tty.setraw(sys.stdin.fileno())

        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)

        if rlist:
            key = sys.stdin.read(1)

            if key == '\x1b':
                key += sys.stdin.read(2)

        else:
            key = ''

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        self.settings = termios.tcgetattr(sys.stdin)

        try:
            while rclpy.ok():

                key = self.get_key()
                cmd = Twist()

                if key == '\x1b[A':      # UP arrow
                    cmd.linear.x = self.linear_speed
                    cmd.angular.z = 0.0

                elif key == '\x1b[B':    # DOWN arrow
                    cmd.linear.x = -self.linear_speed
                    cmd.angular.z = 0.0

                elif key == '\x1b[D':    # LEFT arrow
                    cmd.linear.x = 0.0
                    cmd.angular.z = self.angular_speed

                elif key == '\x1b[C':    # RIGHT arrow
                    cmd.linear.x = 0.0
                    cmd.angular.z = -self.angular_speed

                elif key == 'q':
                    self.get_logger().info('Stopping keyboard attack node')
                    break

                else:
                    cmd.linear.x = 0.0
                    cmd.angular.z = 0.0

                self.publisher.publish(cmd)

        finally:
            stop_cmd = Twist()
            self.publisher.publish(stop_cmd)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


def main(args=None):
    rclpy.init(args=args)

    node = KeyboardAttackNode()

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
