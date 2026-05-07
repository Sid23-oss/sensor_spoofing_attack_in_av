#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
import random


class UltrasonicSensorNode(Node):

    def __init__(self):
        super().__init__('ultrasonic_sensor_node')

        self.front_pub = self.create_publisher(Range, '/ultrasonic_real/front', 10)
        self.left_pub = self.create_publisher(Range, '/ultrasonic_real/left', 10)
        self.right_pub = self.create_publisher(Range, '/ultrasonic_real/right', 10)
        self.rear_pub = self.create_publisher(Range, '/ultrasonic_real/rear', 10)

        self.timer = self.create_timer(0.2, self.publish_sensor_data)

        self.get_logger().info('Raw ultrasonic sensor node started')

    def make_msg(self, frame_id, distance):
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.5
        msg.min_range = 0.02
        msg.max_range = 4.0
        msg.range = distance
        return msg

    def publish_sensor_data(self):
        front = random.uniform(0.8, 4.0)
        left = random.uniform(0.8, 4.0)
        right = random.uniform(0.8, 4.0)
        rear = random.uniform(0.8, 4.0)

        self.front_pub.publish(self.make_msg('front_ultrasonic_raw', front))
        self.left_pub.publish(self.make_msg('left_ultrasonic_raw', left))
        self.right_pub.publish(self.make_msg('right_ultrasonic_raw', right))
        self.rear_pub.publish(self.make_msg('rear_ultrasonic_raw', rear))

        self.get_logger().info(
            f'RAW F={front:.2f} L={left:.2f} R={right:.2f} Rr={rear:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicSensorNode()

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
