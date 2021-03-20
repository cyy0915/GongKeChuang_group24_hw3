# coding: utf8
import rospy
import numpy as np
from geometry_msgs.msg import Twist

def doBlue(myGuide, myVision):
    print('blue')
    position = {'x': 13, 'y' : -4.55}
    quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
    sucess = myGuide.autoGuide(position, quaternion, type=1)
    if sucess:
        print('到达目的地，开始微调')
        while True:
            scanCoordinate = myGuide.getCartesianCoordinate()[240:480]
            result = np.polyfit(scanCoordinate[...,0], scanCoordinate[...,1], 1)
            if result[0]>0.02:
                msg = Twist()
                msg.angular.z = 0.1
                myGuide.goByCommand(msg, 0.1)
            elif result[0]<-0.02:
                msg = Twist()
                msg.angular.z = -0.1
                myGuide.goByCommand(msg, 0.1)
            else:
                break
        myGuide.goStraightNoStop(0.2)
        print('对接完成，等5秒，离开房间')
        rospy.sleep(5)
        for i in range(400):
            myGuide.wallFollowing(reverse = True)
            rospy.sleep(0.1)
        print('任务结束')
