import rospy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import numpy as np 
from math import *
from geometry_msgs.msg import Pose

ball_color = 'blue'

color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 35]), 'Upper': np.array([90, 255, 255])},
              }

class Vision:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher('table_detect_test',Image,queue_size = 10)
        self.image_sub = rospy.Subscriber('/camera/rgb/image_raw',Image,self.callback)
        self.currentColor = None
        self.update = False
        self.image = None

    def callback(self, data):
        self.image = self.bridge.imgmsg_to_cv2(data,"bgr8")
        self.update = True

    def recognizeColor(self):
        if self.update:
            self.update = False
            g_image = cv2.GaussianBlur(self.image, (5, 5), 0)
            hsv = cv2.cvtColor(g_image, cv2.COLOR_BGR2HSV)
            erode_hsv = cv2.erode(hsv, None, iterations=2)
            colorList = ['red', 'blue', 'green']
            for i in colorList:
                if self.haveColor(erode_hsv, i):
                    self.currentColor = i
                    return i
            self.currentColor = None
            return None
        else:
            return self.currentColor

    def haveColor(self, erode_hsv, color):
        inRange_hsv = cv2.inRange(erode_hsv, color_dist[color]['Lower'], color_dist[color]['Upper'])
        count = np.count_nonzero(inRange_hsv)
        if count > 100:
            return True
        else:
            return False

