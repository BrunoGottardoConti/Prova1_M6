import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import queue
import threading
import sys

class CommandQueueNode(Node):
    def __init__(self):
        super().__init__('command_queue_node')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.queue = queue.Queue()
        self.currently_executing = False
        self.queue_thread = threading.Thread(target=self.process_queue)
        self.queue_thread.start()

    def process_queue(self):
        while rclpy.ok():
            if not self.queue.empty() and not self.currently_executing:
                command = self.queue.get()
                self.execute_command(command)
            else:
                stop_msg = Twist()
                self.publisher_.publish(stop_msg)
            rclpy.spin_once(self, timeout_sec=0.1)

    def execute_command(self, command):
        self.currently_executing = True
        vx, vy, vtheta, tempo_ms = command
        msg = Twist()
        msg.linear.x = vx
        msg.linear.y = vy
        msg.angular.z = vtheta
        self.publisher_.publish(msg)
        self.get_logger().info(f'Executing command: vx={vx}, vy={vy}, vtheta={vtheta}, tempo_ms={tempo_ms}')
        self.create_timer(tempo_ms / 1000.0, self.finish_command)

    def finish_command(self):
        self.currently_executing = False

def main(args=None):
    rclpy.init(args=args)

    node = CommandQueueNode()

    try:
        while rclpy.ok():
            input_command = input("Enter command (vx vy vtheta tempo_ms): ")
            vx, vy, vtheta, tempo_ms = map(float, input_command.split())
            node.queue.put((vx, vy, vtheta, tempo_ms))
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        node.queue_thread.join()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
