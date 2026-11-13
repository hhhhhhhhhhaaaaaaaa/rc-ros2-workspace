import rclpy
import asyncio
from rclpy.node import Node
from rclpy.action import ActionClient, GoalResponse,CancelResponse
from geometry_msgs.msg import Point, Twist
from rc_msgs.action import MoveRobot

class MoveRobotActionClient(Node):
    def __init__(self):
        super().__init__("move_robot_action_client")
        self.action_client = ActionClient(self, MoveRobot, "move_robot")
    def send_goal(self,goal):
        goal_msg = MoveRobot.Goal()
        goal_msg.start = goal

        if not self.action_client.wait_for_server(timeout=5.0):
            self.get_logger().error("服务器未响应")
            return
        self.send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        self.get_logger().info("发送目标")
        self.send_goal_future.add_done_callback(self.goal_response_callback)
        self.get_logger().info("等待目标响应")
    def goal_response_callback(self,goal_handle):
        if goal_handle.accepted:
            self.get_logger().info("目标已被接受")
            self.get_result_future = goal_handle.get_result_async()
            self.get_result_future.add_done_callback(self.get_result_callback)
        else:
            self.get_logger().info("目标未被接受")
            return
    def get_result_callback(self,result):
        self.get_logger().info(f"是否成功: {result.result.success}")
        self.get_logger().info("目标执行完成")
    def feedback_callback(self,feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"速度反馈: {feedback.goal_vel.linear}")
        self.get_logger().info(f"目标位置: {feedback.goal}")
def main(args=None):
    rclpy.init(args=args)
    node= MoveRobotActionClient()
    node.send_goal(True)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


    
    
       
