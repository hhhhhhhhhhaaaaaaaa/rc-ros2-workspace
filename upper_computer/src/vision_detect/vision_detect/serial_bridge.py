import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import struct


class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.get_logger().info('串口桥接节点已启动')

    def cmd_cb(self, msg):
        vx = msg.linear.x
        vy = msg.linear.y
        payload = struct.pack('<ff', vx, vy)
        checksum = (0xAA + 0x55 + sum(payload)) & 0xFF
        frame = b'\xAA\x55' + payload + bytes([checksum]) + b'\x0D\x0A'
        self.ser.write(frame)
        self.get_logger().info(f'发送: vx={vx:.3f}, vy={vy:.3f}')


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.ser.close()
        node.destroy_node()
        rclpy.shutdown()
