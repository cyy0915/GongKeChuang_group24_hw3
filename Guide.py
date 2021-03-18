import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Pose, Point, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
import numpy as np
import math

# 自己写的Guide()类，还没写完，大家可以自行修改使用
# cmd_vel 直接命令
# move_base 导航client
class Guide():
    def __init__(self):
        rospy.init_node('guide_test')
        rospy.Subscriber('/scan', LaserScan, self.callback)
        rospy.on_shutdown(self.shutdown)
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.hz = 10
        self.rate = rospy.Rate(self.hz)
        rospy.sleep(1)
        success = self.move_base.wait_for_server(rospy.Duration(5))
        print(success)
        rospy.loginfo("Start")
    
    # 直走遇到障碍物停下
    def goStraightNoStop(self, stopDistance = 0.5):
        move_cmd = Twist()
        move_cmd.linear.x = 0.2
        move_cmd.angular.z = 0
        while self.getFrontDistance() > stopDistance:
            self.cmd_vel.publish(move_cmd)
            self.rate.sleep()
        self.cmd_vel.publish(Twist())

    # 沿墙走，算法还有问题
    def goByWall(self, keepDistanceD = 0.4, keepDistanceU = 0.7):
        move_cmd = Twist()
        move_cmd.linear.x = 0.2
        move_cmd.angular.z = 0
        rotate_cmd = Twist()
        rotate_cmd.linear.x = 0
        rotate_cmd.angular.z = 0.5
        rrotate_cmd = Twist()
        rrotate_cmd.linear.x = 0
        rrotate_cmd.angular.z = -0.5
        lcount = 0
        rcount = 0
        while True:
            if self.getAverageDistance(170,190) > keepDistanceD and self.getAverageDistance(170,190) < keepDistanceU:
                self.cmd_vel.publish(move_cmd)
            elif self.getAverageDistance(170,190) < keepDistanceD and rcount == 0:
                self.cmd_vel.publish(rotate_cmd)
                lcount = 10
            elif lcount == 0:
                self.cmd_vel.publish(rrotate_cmd)
                rcount = 10
            self.rate.sleep()
            if lcount > 0:
                lcount -= 1
            if rcount > 0:
                rcount -= 1

    # 直接命令
    def goByCommand(self, command, time):
        for i in range(int(self.hz*time)):
            self.cmd_vel.publish(command)
            self.rate.sleep()
        self.cmd_vel.publish(Twist())

    # 自动导航，当type=0时pos和quat是相对位置，type=1时是绝对位置
    def autoGuide(self, pos, quat, type = 0):
        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        if type == 0:
            goal.target_pose.header.frame_id = 'base_link'
        else:
            goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
                                     Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

	    # Start moving
        self.move_base.send_goal(goal)
        rospy.sleep(1)
	    # Allow TurtleBot up to 60 seconds to complete task
        success = self.move_base.wait_for_result(rospy.Duration(60)) 

        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    # 计算正前方20度的平均距离
    def getFrontDistance(self):
        return self.getAverageDistance(350,370)
    
    # 计算任意范围的平均距离
    def getAverageDistance(self, start, end):
        return np.mean(np.array(self.scanMsg.ranges[start:end]))

    # scanMsg 激光雷达数据，正负90度共720个数据
    def callback(self,msg):
        self.scanMsg = msg
    
    def shutdown(self):
        self.move_base.cancel_goal()
        self.cmd_vel.publish(Twist())





