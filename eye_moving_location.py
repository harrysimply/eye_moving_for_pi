from eye_moving_stabilize import stabilize
import cv2
import numpy as np

def pupil_location(eye, img, gray, points, RECORD):
    # 通过68个特征点寻找眼睛部位，并且将眼睛框起来
    l = abs(eye[3, 0] - eye[0, 0])  # 两只眼角的长度作为宽度
    # 确定topleft的坐标
    # tl = (eye[0, 0], eye[0, 1] - int(l / 2))
    # br = (eye[3, 0], eye[3, 1] + int(l / 2))
    tl = (
        int(eye[5, 0] + (eye[4, 0] - eye[5, 0]) / 2 - l / 2), int(eye[5, 1] - (eye[5, 1] - eye[1, 1]) / 2 - l / 2))
    crop = gray[tl[1]:(tl[1] + l), tl[0]:(tl[0] + l)]

    gb = cv2.GaussianBlur(crop, (5, 5), 15)
    ret, th1 = cv2.threshold(gb, 50, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
    opening = cv2.morphologyEx(th1, cv2.MORPH_OPEN, kernel)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel2)
    canny = cv2.Canny(closing, 60, 150)
    # cv2.imshow("canny", canny)
    circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 2, 40, param1=30, param2=30, minRadius=0, maxRadius=20)
    # print(circles)
    # if circles!=None:
    tracker = []
    if np.all(circles != None):
        # print("检测到瞳孔！")
        # return circles[0]
        for circle in circles[0]:

            x = int(circle[0])
            y = int(circle[1])
            r = int(circle[2])
            points.extend([(x, y)])
            # print(points)
            flag = 1
            if len(points) == flag:
                # flag调整定位精度
                xy = stabilize(points)
                x = int(xy[0])
                y = int(xy[1])
                # 由于眼动采集时驾驶人来回的移动，导致像素框的大小在记录时不一致，因此坐标值都处于此时的眼睛框大长度做归一化处理
                tracker = [float('%.3f' % (x / l - 0.5)), float('%.3f' % (1 - y / l - .5))]
                RECORD.extend([[float('%.3f' % (x / l - .5)), float('%.3f' % (1 - y / l - .5))]])
                crop = cv2.line(crop, (0, y), (l, y), (255, 255, 255), 1)
                crop = cv2.line(crop, (x, 0), (x, l), (255, 255, 255), 1)
                crop = cv2.circle(crop, (x, y), 2, (0, 0, 255), -1)
                xx = tl[0] + x
                yy = tl[1] + y
                img = cv2.circle(img, (xx, yy), 2, (0, 0, 255), -1)
                points = []

    return tracker, crop, points, RECORD