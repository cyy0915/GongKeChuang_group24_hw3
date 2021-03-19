from Guide import Guide
from Vision import Vision
from DoBlue import doBlue
from DoGreen import doGreen
from DoRed import doRed
import rospy
import threading

def wallFollowingUntilColor(myGuide, myVision):
    while True:
        color = myVision.recognizeColor()
        myGuide.wallFollowing()
        if color is not None:
            return color
        else:
            rospy.sleep(0.05)


myGuide = Guide()
myVision = Vision()
rospy.sleep(1)
color = wallFollowingUntilColor(myGuide, myVision)
if color == 'blue':
    doBlue(myGuide, myVision)
elif color == 'green':
    doGreen(myGuide, myVision)
elif color == 'red':
    doRed(myGuide, myVision)