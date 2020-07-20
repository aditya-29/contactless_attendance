import cv2 as cv
from time import localtime, strftime
import os

class Camera(object):
    CAPTURES_DIR = "../dataset/"
    RESIZE_RATIO = 1.0

    def __init__(self):
        print("[INFO] camera initialized")
        self.video = cv.VideoCapture(0)
    
    def __del__(self):
        print("[INFO] camera ended")
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            print("[INFO]  not success")
            return None

        if (Camera.RESIZE_RATIO != 1):
            frame = cv.resize(frame, None, fx=Camera.RESIZE_RATIO, \
                fy=Camera.RESIZE_RATIO)       
        return frame

    def get_feed(self):
        frame = self.get_frame()
        if frame is not None:
            ret, jpeg = cv.imencode('.jpg', frame)
            return jpeg.tobytes(), ""

    def capture(self, id):
        frame = self.get_frame()
        timestamp = strftime("%d-%m-%Y-%Hh%Mm%Ss", localtime())
        path = Camera.CAPTURES_DIR + str(id) +  "/"
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        no = len(os.listdir(path))
        filename = path + str(no) +".jpg"

        print("[INFO]  FILENAME :", filename)
        print("[INFO] size : ", type(frame))

        if not cv.imwrite(filename, frame):
            raise RuntimeError("Unable to capture image "+timestamp)
        return timestamp