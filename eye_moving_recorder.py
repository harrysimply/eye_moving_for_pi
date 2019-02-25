from eye_ui_pi import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox
import dlib
import sys
import cv2
import numpy as np
from PyQt5.QtGui import QImage,QPixmap
from eye_moving_location import  pupil_location
from PyQt5.QtCore import QTimer,QCoreApplication
from datetime import datetime

class mainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer_1=QTimer()
        self.timer_1.setInterval(1)

        btn_start=self.ui.toolButton_2
        btn_save =self.ui.toolButton_3
        btn_close=self.ui.toolButton_4

        btn_start.clicked.connect(self.open_camera)
        btn_close.clicked.connect(QCoreApplication.instance().quit)
        btn_save.clicked.connect(self.save_data)

        self.init_lib()

    def init_lib(self):
        self.detector = dlib.get_frontal_face_detector()  # 检测人脸
        predictor_path = "./shape_predictor_68_face_landmarks.dat"
        self.predictor = dlib.shape_predictor(predictor_path)  # 68个特征点提取器
        # 初始化dlib中的人脸特征点排号
        self.RIGHT_EYE_START = 37 - 1
        self.RIGHT_EYE_END = 42 - 1
        self.LEFT_EYE_START = 43 - 1
        self.LEFT_EYE_END = 48 - 1
        # 初始化瞳孔定位的一些初值
        self.l_points = []
        self.l_RECORD = []
        self.r_points = []
        self.r_RECORD = []
        self.left_eye_crop = []
        self.right_eye_crop = []

    def open_camera(self):
        self.starttime = datetime.now().strftime('%y_%m_%d_%H_%M_%S')
        self.capture = cv2.VideoCapture(0)
        self.timer_1.timeout.connect(self.capture_picture)
        self.timer_1.start()
    def capture_picture(self):
        ret,img = self.capture.read()
        if ret:
            img = cv2.flip(img,1,dst=None)
            self.height, self.width, bytesPerComponent = img.shape
            bytesPerLine = 3 * self.width
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转成灰度图像
            dets = self.detector(gray, 0)

            for i, d in enumerate(dets):
                shape = self.predictor(img, d)
                landmarks = np.matrix([[p.x, p.y] for p in shape.parts()])
                left_eye = landmarks[self.LEFT_EYE_START:self.LEFT_EYE_END + 1]
                right_eye = landmarks[self.RIGHT_EYE_START:self.LEFT_EYE_END + 1]

                #左眼（翻转）
                l_tracker, self.left_eye_crop, self.l_points, self.l_RECORD = pupil_location(left_eye, img, gray, self.l_points, self.l_RECORD)
                l_height, l_width = self.left_eye_crop.shape
                l_bytesPerLine = 1 * l_width
                l_QImg = QImage(bytes(self.left_eye_crop.data), l_width, l_height, l_bytesPerLine,
                                QImage.Format_Indexed8)
                l_pixmap = QPixmap.fromImage(l_QImg).scaled(self.ui.label_3.width(), self.ui.label_3.height())

                self.ui.label_3.setPixmap(l_pixmap)

                #右眼（翻转）
                r_tracker, self.right_eye_crop, self.r_points, self.r_RECORD = pupil_location(right_eye, img, gray,
                                                                                             self.r_points,
                                                                                             self.r_RECORD)
                r_height, r_width = self.right_eye_crop.shape
                r_bytesPerLine = 1 * r_width
                r_QImg = QImage(bytes(self.right_eye_crop.data), r_width, r_height, r_bytesPerLine,
                                QImage.Format_Indexed8)
                r_pixmap = QPixmap.fromImage(r_QImg).scaled(self.ui.label_2.width(), self.ui.label_2.height())

                self.ui.label_2.setPixmap(r_pixmap)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            QImg = QImage(img.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg).scaled(self.ui.label.width(), self.ui.label.height())
            self.ui.label.setPixmap(pixmap)
            #print(self.l_RECORD)
            #print(self.r_RECORD)

    def save_data(self):
        self.capture.release()
        self.timer_1.stop()
        import os
        if not os.path.exists('./data'):
            os.makedirs('./data')
            print("True")

        from datetime import datetime
        endtime = datetime.now().strftime('%H_%M_%S')
        # right_txt = "/home/hx-104b/eye_tracking_for_pi/data/record_right_eye_{}-{}.txt".format(self.starttime, endtime)
        # left_txt = "/home/hx-104b/eye_tracking_for_pi/data/record_left_eye_{}-{}.txt".format(self.starttime, endtime)
        eyes_dirs="./data/record_{}-{}".format(self.starttime, endtime)
        os.makedirs(eyes_dirs)
        right_txt = "{}/record_right_eye_{}-{}.txt".format(eyes_dirs,self.starttime, endtime)
        left_txt = "{}/record_left_eye_{}-{}.txt".format(eyes_dirs,self.starttime, endtime)
        with open(right_txt,"w") as f:
            for i in self.l_RECORD:
                f.writelines(str(i))
                f.writelines('\n')
        with open(left_txt,"w") as f:
            for i in self.r_RECORD:
                f.writelines(str(i))
                f.writelines('\n')
        QMessageBox.information(self, "Done!", "眼动轨迹数据已经成功写入文件{}和{}.".format(right_txt,left_txt), QMessageBox.Yes)


if __name__=='__main__':
    app=QApplication(sys.argv)
    window=mainWindow()
    window.show()


    sys.exit(app.exec_())

