import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Twist, Point
from rc_msgs.msg import YoloOutputArray
from rc_msgs.action import MoveRobot
from rclpy.executors import MultiThreadedExecutor
import time


class MoveRobotActionServer(Node):
    def __init__(self):
        super().__init__('move_robot_action_server')
        self.action_server = ActionServer(
            self, MoveRobot, 'move_robot', self.execute_callback)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.latest_center = None
        self.sub = self.create_subscription(
            YoloOutputArray, 'position_data', self.center_callback, 10)
        # PID 参数
        self.kp, self.ki, self.kd = 0.005, 0.0002, 0.0005
        self.img_cx, self.img_cy = 320.0, 240.0
        self.get_logger().info('MoveRobot 服务端已就绪')

    def center_callback(self, msg):
        if len(msg.yolo_array) > 0:
            self.latest_center = (
                msg.yolo_array[0].center_x,
                msg.yolo_array[0].center_y)
        else:
            self.latest_center = None

    def pid(self, err, state):
        state['i'] = max(-1000.0, min(1000.0, state['i'] + err))
        d = err - state['prev']
        state['prev'] = err
        out = self.kp * err + self.ki * state['i'] + self.kd * d
        return max(-1.0, min(1.0, out))

    def execute_callback(self, goal_handle):
        request = goal_handle.request
        if not request.start:
            goal_handle.abort()
            result = MoveRobot.Result()
            result.success = False
            return result

        self.get_logger().info('收到 start=True，开始伺服')
        state_x = {'i': 0.0, 'prev': 0.0}
        state_y = {'i': 0.0, 'prev': 0.0}
        twist = Twist()
        feedback_msg = MoveRobot.Feedback()

        err_x = err_y = 999.0
        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.cmd_pub.publish(Twist())
                return goal_handle.get_result()

            if self.latest_center is None:
                time.sleep(0.05)
                continue

            cx, cy = self.latest_center
            err_x = cx - self.img_cx
            err_y = cy - self.img_cy

            twist.linear.y = self.pid(err_x, state_x)
            twist.linear.x = self.pid(err_y, state_y)
            self.cmd_pub.publish(twist)

            feedback_msg.is_running = True
            feedback_msg.goal = Point(x=cx, y=cy, z=0.0)
            feedback_msg.goal_vel = twist
            goal_handle.publish_feedback(feedback_msg)

            if abs(err_x) < 10.0 and abs(err_y) < 10.0:
                break
            time.sleep(0.05)

        self.cmd_pub.publish(Twist())
        if abs(err_x) < 10.0 and abs(err_y) < 10.0:
            goal_handle.succeed()
            result = MoveRobot.Result()
            result.success = True
        else:
            goal_handle.abort()
            result = MoveRobot.Result()
            result.success = False
        return result


def main(args=None):
    rclpy.init(args=args)
    node = MoveRobotActionServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()