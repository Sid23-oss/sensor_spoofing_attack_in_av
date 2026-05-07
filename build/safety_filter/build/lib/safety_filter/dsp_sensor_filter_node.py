#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from collections import deque
import statistics


class DSPSensorFilterNode(Node):

    def __init__(self):
        super().__init__('dsp_sensor_filter_node')

        self.sensor_names = ['front', 'left', 'right', 'rear']

        self.raw_values = {
            'front': 4.0,
            'left': 4.0,
            'right': 4.0,
            'rear': 4.0
        }

        self.filtered_values = {
            'front': 4.0,
            'left': 4.0,
            'right': 4.0,
            'rear': 4.0
        }

        self.history = {
            name: deque(maxlen=5)
            for name in self.sensor_names
        }

        self.attack_flags = {
            name: False
            for name in self.sensor_names
        }

        self.min_range = 0.02
        self.max_range = 4.0

        # DSP filter parameters
        self.alpha = 0.35          # EMA smoothing factor
        self.max_jump = 1.2        # max allowed sudden jump per sample
        self.min_valid = 0.02
        self.max_valid = 4.0

        self.publishers = {}

        for name in self.sensor_names:

            self.create_subscription(
                Range,
                f'/ultrasonic_raw/{name}',
                lambda msg, sensor=name: self.sensor_callback(msg, sensor),
                10
            )

            self.publishers[name] = self.create_publisher(
                Range,
                f'/ultrasonic/{name}',
                10
            )

        self.timer = self.create_timer(0.2, self.publish_filtered_data)

        self.get_logger().info('DSP sensor filter node started')
        self.get_logger().info('Subscribing raw sensors and publishing protected sensors')

    def sensor_callback(self, msg, sensor_name):
        value = msg.range

        self.raw_values[sensor_name] = value

        previous = self.filtered_values[sensor_name]

        attack_detected = False

        # Rule 1: physical range check
        if value < self.min_valid or value > self.max_valid:
            attack_detected = True

        # Rule 2: sudden jump detection
        if abs(value - previous) > self.max_jump:
            attack_detected = True

        # Store history only if physically valid
        if self.min_valid <= value <= self.max_valid:
            self.history[sensor_name].append(value)

        # Median filter
        if len(self.history[sensor_name]) >= 3:
            median_value = statistics.median(self.history[sensor_name])
        else:
            median_value = previous

        if attack_detected:
            # Reject spoofed value
            clean_value = previous
            self.attack_flags[sensor_name] = True

            self.get_logger().warn(
                f'ATTACK DETECTED on {sensor_name}: raw={value:.2f}, keeping={previous:.2f}'
            )

        else:
            # EMA low-pass filter
            clean_value = (self.alpha * median_value) + ((1.0 - self.alpha) * previous)
            self.attack_flags[sensor_name] = False

        self.filtered_values[sensor_name] = clean_value

    def make_msg(self, sensor_name, value):
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = sensor_name + '_ultrasonic_filtered'
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.5
        msg.min_range = self.min_range
        msg.max_range = self.max_range
        msg.range = value
        return msg

    def publish_filtered_data(self):

        for name in self.sensor_names:
            msg = self.make_msg(name, self.filtered_values[name])
            self.publishers[name].publish(msg)

        self.get_logger().info(
            f'FILTERED '
            f'F={self.filtered_values["front"]:.2f} '
            f'L={self.filtered_values["left"]:.2f} '
            f'R={self.filtered_values["right"]:.2f} '
            f'Rear={self.filtered_values["rear"]:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = DSPSensorFilterNode()

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
