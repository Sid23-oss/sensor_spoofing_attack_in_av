#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class DSPFilterEnableNode(Node):

    def __init__(self):
        super().__init__('dsp_filter_node')

        self.pub = self.create_publisher(
            Bool,
            '/dsp_filter_enable',
            10
        )

        self.timer = self.create_timer(
            0.2,
            self.publish_enable
        )

        self.get_logger().info('DSP FILTER ENABLED')

    def publish_enable(self):
        msg = Bool()
        msg.data = True
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DSPFilterEnableNode()

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
