# coding: utf8
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Pose, Point, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
import numpy as np
import math
from nav_msgs.msg import Odometry
from tf import transformations
import threading
import cmath

# 自己写的Guide()类，还没写完，大家可以自行修改使用
# cmd_vel 直接命令
# move_base 导航client
class Guide():
    def __init__(self):
        rospy.init_node('guide_test')
        rospy.Subscriber('/scan', LaserScan, self.laserScanCall)
        rospy.on_shutdown(self.shutdown)
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.hz = 10
        self.rate = rospy.Rate(self.hz)
        self.scanCoordinate = None
        rospy.sleep(1)
        success = self.move_base.wait_for_server(rospy.Duration(5))
        print(success)

        # wall following variables
        self.pub = None
        self.regions = {
            'fright': 0,
            'front': 0,
            'fleft': 0,
        }
        self.state = 0

        rospy.loginfo("Start")
    
    # 直走遇到障碍物停下
    def goStraightNoStop(self, stopDistance = 0.5):
        move_cmd = Twist()
        move_cmd.linear.x = 0.1
        move_cmd.angular.z = 0
        while self.getFrontDistance() > stopDistance:
            self.cmd_vel.publish(move_cmd)
            self.rate.sleep()
        self.cmd_vel.publish(Twist())

    def changeStateInWallFollowing(self, state):
        if state != self.state:
            #print 'Wall follower - [%s] - %s' % (state, self.state_dict[state])
            self.state = state

    def determineStateInWallFollowing(self, reverse = False):
        self.regions = {
            'fright': min(min(self.scanMsg.ranges[144:287]), 10),
            'front':  min(min(self.scanMsg.ranges[288:431]), 10),
            'fleft':  min(min(self.scanMsg.ranges[432:575]), 10),
        }
        regions = self.regions
        state_description = ''
        
        d = 0.7
        if reverse:
            if regions['front'] < d:
                state_description = 'case 1 - need to turn right'
                self.changeStateInWallFollowing(1)
            elif regions['fleft'] > d:
                state_description = 'case 2 - need to turn left'
                self.changeStateInWallFollowing(0)
            else: 
                state_description = 'case 3 - follow the wall'
                self.changeStateInWallFollowing(2)
        else:
            if regions['front'] < d:
                state_description = 'case 1 - need to turn left'
                self.changeStateInWallFollowing(1)
            elif regions['fright'] > d:
                state_description = 'case 2 - need to turn right'
                self.changeStateInWallFollowing(0)
            else: 
                state_description = 'case 3 - follow the wall'
                self.changeStateInWallFollowing(2)

    def wallFollowing(self, reverse = False):
        self.determineStateInWallFollowing(reverse)
        if reverse:
            if self.state == 0:
                self.turn_left_r()
            elif self.state == 1:
                self.turn_right_r()
            elif self.state == 2:
                self.follow_the_wall()
            else:
                rospy.logerr('Unknown state!')
        else:
            if self.state == 0:
                self.turn_right()
            elif self.state == 1:
                self.turn_left()
            elif self.state == 2:
                self.follow_the_wall()
            else:
                rospy.logerr('Unknown state!')
    
    def turn_right(self):
        msg = Twist()
        msg.linear.x = 0.15
        msg.angular.z = -0.3
        self.cmd_vel.publish(msg)

    def turn_left(self):
        msg = Twist()
        msg.angular.z = 0.3
        self.cmd_vel.publish(msg)

    def turn_right_r(self):
        msg = Twist()
        msg.angular.z = -0.3
        self.cmd_vel.publish(msg)

    def turn_left_r(self):
        msg = Twist()
        msg.linear.x = 0.15
        msg.angular.z = 0.3
        self.cmd_vel.publish(msg)

    def follow_the_wall(self):
        msg = Twist()
        msg.linear.x = 0.5
        self.cmd_vel.publish(msg)

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
        success = self.move_base.wait_for_result(rospy.Duration(120)) 

        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        self.cmd_vel.publish(Twist())
        return result

    # 计算正前方20度的平均距离
    def getFrontDistance(self):
        return self.getAverageDistance(350,370)
    
    # 计算任意范围的平均距离
    def getAverageDistance(self, start, end):
        return np.mean(np.array(self.scanMsg.ranges[start:end]))

    # scanMsg 激光雷达数据，正负90度共720个数据
    def laserScanCall(self,msg):
        self.scanMsg = msg
    
    def getCartesianCoordinate(self):
        self.scanCoordinate = np.zeros([720,2])
        for i in range(720):
            tmp = cmath.rect(self.scanMsg.ranges[i], i * cmath.pi/720)
            self.scanCoordinate[i] = [tmp.real, tmp.imag]
        return self.scanCoordinate
            
    def shutdown(self):
        self.move_base.cancel_goal()
        self.cmd_vel.publish(Twist())





