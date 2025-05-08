import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory,JointTrajectoryPoint 
import time

class KinovaControl(Node):
    def __init__(self):
        super().__init__('kinova_coomander')
        self.publisher = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory' ,10)
        self.trajectory_msg = JointTrajectory()
        self.trajectory_msg.joint_names = ['joint_1' ,'joint_2' ,'joint_3' ,'joint_4' ,'joint_5' ,'joint_6', 'joint_7']
        point = JointTrajectoryPoint()
        point.positions = [0.0, -0.0, 0.0, 0.0, 0.0, 0.5, 0.0]
        point.time_from_start.sec = 3

        self.trajectory_msg.points.append(point)

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('Node successfully initialiized!')
        
    
    def timer_callback(self):
        self.publisher.publish(self.trajectory_msg)
        time.sleep(10)


def main(args = None):
    rclpy.init(args = args)
    node = KinovaControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
