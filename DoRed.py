import time
import numpy as np
import matplotlib.pyplot as plt
import cmath


def doRed(myGuide, myVision):
    print ("It is red.")

    # ######  Go to the bed  ################
    position = {"x": 7.7, "y": -13.7}
    quaternion = {"r1": 0.000, "r2": 0.000, "r3": -1.000, "r4": 0.000}
    myGuide.autoGuide(position, quaternion, 1)
    time.sleep(3)
    # ######  get length of bed  ###############
    index = np.zeros([720])
    distance = np.zeros([720])
    x = 0  # The right side of the bed
    xEnd = 0  # The left side of the bed
    for i in range(720):
        index[i] = i * cmath.pi / 720
        distance[i] = myGuide.scanMsg.ranges[719 - i]
        if distance[i] > 2:
            x = i
            # print(i, index[i], distance[i])
            break
    for i in range(x - 1):
        if abs(distance[i + 1] - distance[i]) > 0.1:
            xEnd = i + 1
            # print(i, distance[i+1]-distance[i])
            break
    index = index[xEnd:x:1]
    distance = distance[xEnd:x:1]
    y = np.zeros(x - xEnd)
    for i in range(x - xEnd):
        tmp = cmath.rect(distance[i], i * cmath.pi / 720)
        index[i] = tmp.real
        y[i] = tmp.imag
    z = np.polyfit(index, y, 1)
    k = z[0]
    b = z[1]
    # yHat = np.zeros(x-xEnd)
    # for i in range(x-xEnd):
    #     yHat[i] = k*index[i]+b
    lengthOfBed = (abs(index[x - xEnd - 1] - index[0]) * cmath.sqrt(1 + k ** 2)).real
    print "The Length of the bed is:", lengthOfBed
    # ######  plot the results  #################
    # plt.figure()
    # plt.scatter(index, y, c='b', marker='.')
    # # plt.plot(index, yHat, 'r')
    # plt.show()
    # ######  get out of the room  ##############
    time.sleep(3)
    position = {"x": 8.5, "y": -8}
    myGuide.autoGuide(position, quaternion, 1)
