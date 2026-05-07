#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from std_msgs.msg import Bool


class SensorRouterNode(Node):

    def __init__(self):
        super().__init__('sensor_router_node')

        self.names = ['front', 'left', 'right', 'rear']

        self.real = {name: 4.0 for name in self.names}
        self.attack = {name: 4.0 for name in self.names}
        self.filtered = {name: 4.0 for name in self.names}

        self.attack_active = False
        self.protection_enabled = False

        self.alpha = 0.3
        self.max_jump = 1.0

        # Do NOT name this self.publishers
        self.sensor_publishers = {}

        for name in self.names:
            self.create_subscription(
                Range,
                f'/ultrasonic_real/{name}',
                lambda msg, n=name: self.real_callback(msg, n),
                10
            )

            self.create_subscription(
                Range,
                f'/ultrasonic_attack/{name}',
                lambda msg, n=name: self.attack_callback(msg, n),
                10
            )

            self.sensor_publishers[name] = self.create_publisher(
                Range,
                f'/ultrasonic/{name}',
                10
            )

        self.create_subscription(
            Bool,
            '/dsp_filter_enable',
            self.filter_callback,
            10
        )

        self.timer = self.create_timer(0.2, self.route_data)

        self.get_logger().info('Sensor router node started')

    def real_callback(self, msg, name):
        self.real[name] = msg.range

    def attack_callback(self, msg, name):
        self.attack[name] = msg.range
        self.attack_active = True

    def filter_callback(self, msg):
        self.protection_enabled = msg.data

    def make_msg(self, name, value):
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = name + '_ultrasonic'
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.5
        msg.min_range = 0.02
        msg.max_range = 4.0
        msg.range = value
        return msg

    def dsp_filter(self, name, value):
        old = self.filtered[name]

        if abs(value - old) > self.max_jump:
            clean = old
            self.get_logger().warn(
                f'ATTACK BLOCKED on {name}: incoming={value:.2f}, keeping={old:.2f}'
            )
        else:
            clean = self.alpha * value + (1.0 - self.alpha) * old

        self.filtered[name] = clean
        return clean

    def route_data(self):
        mode = 'NORMAL'

        for name in self.names:

            if self.protection_enabled:
                # DSP filter ON: ignore attack and use filtered real sensor data
                output = self.dsp_filter(name, self.real[name])
                mode = 'PROTECTED'

            elif self.attack_active:
                # Attack ON and DSP OFF: attack controls the sensor values
                output = self.attack[name]
                mode = 'ATTACK'

            else:
                # Normal: use real sensor values
                output = self.real[name]
                mode = 'NORMAL'

            self.sensor_publishers[name].publish(
                self.make_msg(name, output)
            )

        self.get_logger().info(
            f'MODE={mode} '
            f'F={self.real["front"]:.2f}/{self.attack["front"]:.2f} '
            f'L={self.real["left"]:.2f}/{self.attack["left"]:.2f} '
            f'R={self.real["right"]:.2f}/{self.attack["right"]:.2f} '
            f'Rear={self.real["rear"]:.2f}/{self.attack["rear"]:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = SensorRouterNode()

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
