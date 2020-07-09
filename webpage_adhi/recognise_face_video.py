# python recognize_faces_video.py --encodings encodings.pickle --output output/jurassic_park_trailer_output.avi --display 0

# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import pandas as pd
from datetime import datetime as dt


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
ap.add_argument("-y", "--display", type=int, default=1,
	help="whether or not to display output frame to screen")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
ap.add_argument("-f", "--file", type=str, required = True,
    help="location of the file")
args = vars(ap.parse_args())

xl_file = args["file"]

time_interval = 10
id_list = pd.read_excel("logs/id_map.xlsx")

entry_list = pd.read_excel(xl_file)
entry_list.fillna("", inplace=True)

def refresh():
    global entry_list
    entry_list = pd.read_excel(xl_file)
    entry_list.fillna("", inplace=True)
    return entry_list

def get_name(id):
    # id = str(id)
    index = id_list.index[id_list["id"]==id].tolist()
    # print(index, type(index))
    return(id_list.iloc[int(index[0]), 1], id_list.iloc[int(index[0]), 2])

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



def update_sheet(id):
    global entry_list

    now = dt.now()
    name, cat = get_name(id)
    print("[INFO] NAME : ", name, " CAT : " ,cat)

    check = check_dup(id, now)
    
    if check == "entry":            #no prev entries
        print("-----------------entry----------------------")

        if entry_list["s.no"].to_list() == []:
            serial_no = 1        
        else:
            serial_no = entry_list["s.no"].to_list()[-1]+1

        row = {"s.no" : serial_no, 
                "name" : name,
                "id" : str(id),
                "category" : cat, 
                "entry_time" : now.strftime("%H:%M:%S"),
                "exit_time" : ""}

        entry_list = entry_list.append(row, ignore_index = True)


        entry_list.to_excel(xl_file, index = False)
        time.sleep(0.5)
        entry_list = refresh()
        print(entry_list.head())
        print("[INFO] time taken to update sheet : ",(dt.now()-now).seconds)
            
    elif check == "exit":           #directs to exit route
        print("---------------exit-------------")
        index = entry_list.index[entry_list["id"] == id].tolist()
        index = int(index[-1])
        entry_list.iloc[index, 5] = now.strftime("%H:%M:%S")

        entry_list.to_excel(xl_file, index = False)
        entry_list = refresh()
        print(entry_list.head())
        print("[INFO] time taken to update sheet : ",(dt.now()-now).seconds)

    else:                                       #duplicate access
        print("")
        print('duplicate person detected')
        print("")


# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
writer = None
time.sleep(2.0)

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
    frame = vs.read()
	
	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = imutils.resize(frame, width=750)
    r = frame.shape[1] / float(rgb.shape[1])

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
    boxes = face_recognition.face_locations(rgb,
        model=args["detection_method"])
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    name = "Unknown"
	# loop over the facial embeddings
    for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
        name = "Unknown"

		# check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
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

	# if the video writer is None *AND* we are supposed to write
	# the output video to disk initialize the writer
    if writer is None and args["output"] is not None:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(args["output"], fourcc, 20,
            (frame.shape[1], frame.shape[0]), True)

	# if the writer is not None, write the frame with recognized
	# faces t odisk
    if writer is not None:
        writer.write(frame)

	# check to see if we are supposed to display the output frame to
	# the screen

    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    if name=="Unknown":
        pass
    else:
        name = int(name)
        update_sheet(name)

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

# check to see if the video writer point needs to be released
if writer is not None:
	writer.release()