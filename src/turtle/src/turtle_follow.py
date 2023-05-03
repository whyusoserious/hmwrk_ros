#!/usr/bin/python

import rospy
import math
import random

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn


class TurtleFollower:
    def __init__(self, turtle1_name, turtle2_name, follower_speed):
        self.turtle1_name = turtle1_name
        self.turtle2_name = turtle2_name
        self.follower_speed = follower_speed
        self.pose1 = Pose()
        self.pose2 = Pose()

        rospy.Subscriber("/" + self.turtle1_name + "/pose", Pose, self.callback1)
        rospy.Subscriber("/" + self.turtle2_name + "/pose", Pose, self.callback2)
        self.pub = rospy.Publisher("/" + self.turtle2_name + "/cmd_vel", Twist, queue_size=10)

        # Spawn the second turtle
        spawner = rospy.ServiceProxy('spawn', Spawn)
        spawner(random.uniform(0, 11), random.uniform(0, 11), 0, turtle2_name)

        # Wait for the second turtle to spawn and get its initial position
        rospy.wait_for_message("/" + self.turtle2_name + "/pose", Pose)
        pose2_msg = rospy.wait_for_message("/" + self.turtle2_name + "/pose", Pose)
        self.pose2.x = pose2_msg.x
        self.pose2.y = pose2_msg.y

    def callback1(self, data):
        self.pose1 = data

    def callback2(self,data):
        self.pose2 = data

    def follow(self):
        while not rospy.is_shutdown():
            x_diff = self.pose1.x - self.pose2.x
            y_diff = self.pose1.y - self.pose2.y
            distance = ((x_diff)**2 + (y_diff)**2)**0.5
            angle_to_target = math.atan2(y_diff, x_diff)
            angle_diff = angle_to_target - self.pose2.theta

            cmd_vel = Twist()
            cmd_vel.linear.x = self.follower_speed * distance
            cmd_vel.angular.z = 4.0 * angle_diff

            self.pub.publish(cmd_vel)
            rospy.sleep(0.1)


if __name__ == '__main__':
    rospy.init_node('turtle_follower_node')

    follower_speed = rospy.get_param('~follower_speed')
    turtle1_name = rospy.get_param('~turtle1_name', 'turtle1')
    turtle2_name = rospy.get_param('~turtle2_name', 'turtle2')

    follower = TurtleFollower(turtle1_name, turtle2_name, follower_speed)
    follower.follow()
