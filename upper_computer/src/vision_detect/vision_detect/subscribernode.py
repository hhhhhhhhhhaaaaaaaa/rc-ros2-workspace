import rclpy
from rclpy.node import Node
from rc_msgs.msg import YoloOutputArray, YoloOutput


class SubscriberNode(Node):
    def __init__(self):
        super().__init__('subscriber_node')
        self.get_logger().info('SubscriberNode is up and running!')
        self.sub = self.create_subscription(
            YoloOutputArray, "position_data", self.callback, 10)

    def callback(self, msg):
        self.get_logger().info(f'Received message: {msg}')
        for item in msg.yolo_array:
            self.get_logger().info(
                f'Center X: {item.center_x}, Center Y: {item.center_y}')


def main(args=None):
    rclpy.init(args=args)
    node = SubscriberNode('subscriber_node')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()