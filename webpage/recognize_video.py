from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time as Time
import cv2
import pandas as pd
from datetime import datetime as dt
import utils as u
from time import time



xl_file = u.logs_check()

iter = 0
temp_names = []
limit_thresh = 10
iter_names = {}


time_interval = 60
users_list = pd.read_excel("../admin/users.xlsx")

entry_list = pd.read_excel(xl_file)
entry_list.fillna("", inplace=True)

def refresh():
    global entry_list
    entry_list = pd.read_excel(xl_file)
    entry_list.fillna("", inplace=True)
    return entry_list

def get_name(id):
    index = users_list.index[(users_list["id"])==(id)].tolist()

    if index == []:
        return None, None
    return(users_list.iloc[index[0], 2], users_list.iloc[int(index[0]), 3])

def check_dup(id,now):
    # id = int(id)
    # entry_list = refresh()
    index = entry_list.index[entry_list["id"] == id].tolist()
    if len(index)==0:           #if there are no prev values
        return "entry"
    else:                        #if there is a prev value
        prev = entry_list.iloc[index[-1], 4]   
        prev = dt.strptime(prev, "%H:%M:%S")
        if (now - prev).seconds > time_interval:
            exit_t_s = entry_list.iloc[index[-1], 5]
            if exit_t_s == "":
                return "exit"
            else:
                exit_t = dt.strptime(exit_t_s, "%H:%M:%S")
                if (now-exit_t).seconds > time_interval:
                    return "entry"
        return None


def update_sheet(id,duplicate_check = True):
    global entry_list

    now = dt.now()
    name, cat = get_name(id)
    if name == None:
        return
    print("[INFO] NAME : ", name, " CAT : " ,cat)

    if duplicate_check:
        check = check_dup(id, now)
    else:
        check = None
    
    if check == "entry":            #no prev entries
        print("-----------------entry----------------------")

        if entry_list["s.no"].to_list() == []:
            serial_no = 1        
        else:
            serial_no = entry_list["s.no"].to_list()[-1]+1

        entry_time = now.strftime("%H:%M:%S")

        row = {"s.no" : serial_no, 
                "name" : name,
                "id" : str(id),
                "category" : cat, 
                "entry_time" : entry_time,
                "exit_time" : ""}

        entry_list = entry_list.append(row, ignore_index = True)


        entry_list.to_excel(xl_file, index = False)
        Time.sleep(0.5)
        entry_list = refresh()
        # print(entry_list.head())
        print("[INFO] time taken to update sheet : ",(dt.now()-now).seconds)
        return {"entry" : entry_time, "exit" : "NILL", "id" : str(id), "name": name, "dup" : "False"}
            
    elif check == "exit":           #directs to exit route
        print("---------------exit-------------")
        index = entry_list.index[entry_list["id"] == id].tolist()
        index = int(index[-1])

        name = entry_list.iloc[index, 1]
        id = entry_list.iloc[index, 2]
        entry_time = entry_list.iloc[index, 4]
        exit_time = now.strftime("%H:%M:%S")

        entry_list.iloc[index, 5] = exit_time

        entry_list.to_excel(xl_file, index = False)
        entry_list = refresh()
        print(entry_list.head())
        print("[INFO] time taken to update sheet : ",(dt.now()-now).seconds)
        return {"entry": entry_time, "exit" : exit_time, "id": str(id), "name": name, "dup" : "False"}

    else:     
        index = entry_list.index[entry_list["id"] == id].tolist()
        index = int(index[-1])

        name = entry_list.iloc[index, 1]
        id = entry_list.iloc[index, 2]
        entry_time = entry_list.iloc[index, 4]
        exit_time = entry_list.iloc[index, 5]                                 #duplicate access
        print("")
        print('duplicate person detected')
        print("")
        return {"entry" : entry_time, "exit" : exit_time, "id" : str(id), "name" : name, "dup": "True"}




class Camera(object):
    CAPTURES_DIR = "../dataset/"
    RESIZE_RATIO = 1.0

    def __init__(self):
        print("[INFO] camera initialized")
        self.video = cv2.VideoCapture(0)
        print("[INFO] loading encodings...")
        self.data = pickle.loads(open("encodings", "rb").read())

        print("[INFO] starting video stream...")
        Time.sleep(2.0)

    
    def __del__(self):
        print("[INFO] camera ended")
        self.video.release()

    def get_feed(self):
        frame,res = self.get_frame()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes(), res

    def get_frame(self):
        global limit_thresh, iter, iter_names
        now = time()
        success, frame = self.video.read()

        if not success:
            return None
        
        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=750)
        r = frame.shape[1] / float(rgb.shape[1])

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input frame, then compute
        # the facial embeddings for each face
        boxes = face_recognition.face_locations(rgb,
            model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        name = "Unknown"
        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(self.data["encodings"],
                encoding)
            name = "Unknown"

            if True in matches:

                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    name = self.data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)
            
            # update the list of names
            names.append(name)

        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # rescale the face coordinates
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
        res = None
        if name=="Unknown":
            if time() - now > 30:
                iter_names = []
                now = time()
            pass
        else:
            now = time()
            print("iter_names : ",iter_names)
            if iter<limit_thresh:
                if name not in iter_names:
                    iter_names[name] = 1
                iter+=1
                iter_names[name]+=1
            else:
                iter = 0
                name =  max(iter_names.keys())
                res = update_sheet(name)
                iter_names = {}
            print(name)
        return frame, res

if __name__ == "__main__":
    pass