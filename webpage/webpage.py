import os
from flask import Flask, request, render_template, Response, url_for, redirect
import utils as u
from camera import Camera
from recognize_video import Camera as Camera_recog
import sys
import encode_faces as ef
import recognize_video as recog

app = Flask(__name__)


camera = None
camera_recog = None
pwd = None

def get_camera():
    global camera
    if not camera:
        camera = Camera()
    # camera = Camera()
    return camera

def get_camera_recog():
    global camera_recog
    if not camera_recog:
        camera_recog = Camera_recog()
    # camera_recog = Camera_recog()
    return camera_recog

@app.route("/")

def main():
    return render_template("index.html")

#retriving auth.xlsx

@app.route("/take_attendance", methods = ["POST", "GET"])

def login():   #cross check the login information
    global pwd

    id = request.form["id"]
    id = str(id)
    name = request.form["username"]
    pwd = request.form["password"]

    res = u.authenticate(id, name, pwd)
    if not res:
        return render_template("/index.html", error="invalid user/password")
    else:
        path = u.logs_check()
        return redirect(url_for("attendance"))

@app.route("/logout", methods = ["POST", "GET"])

def logout():
    return render_template("index.html")


@app.route("/attendance", methods = ["POST", "GET"])

def attendance():
    print("[INFO] attendance thread started")
    path = u.logs_check()
    return render_template("attendance.html")





@app.route("/register", methods = ["POST", "GET"])

def register():
    return render_template("register.html")

def gen(camera):
    while True:
        frame = camera.get_feed()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_recog(camera_recog):
    while True:
        frame = camera_recog.get_feed()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/capture", methods=["POST", "GET"])

def view_page():
    return render_template("capture.html")

@app.route("/manual", methods=["POST", "GET"])

def manual():
    global pwd

    id = request.form["id"]
    id = str(id).upper()
    temp_pwd = request.form["pwd"]

    if temp_pwd == pwd:
        recog.update_sheet(str(id))
        return render_template("./attendance.html", error="Added Successfully")

    else:
        return render_template("./attendance.html", error="invalid admin password")


@app.route('/video_feed')
def video_feed():
    # return ray.get(video_feed_thread.remote())
    print("[INFO] video feed thread started")
    camera = Camera()
    return Response(gen(camera),
        mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/video_feed_attendance")
def video_feed_attendance():
    print("[INFO] video feed thread started")
    camera_recog = Camera_recog()
    return Response(gen(camera_recog),
        mimetype='multipart/x-mixed-replace; boundary=frame')
    

@app.route("/save_pic", methods= ["POST", "GET"])
def capture():
    id = request.form["id"]
    id = str(id).upper()
    temp_pwd = request.form["pwd"]
    if temp_pwd == pwd:
        camera = Camera()
        stamp = camera.capture(id) 
        return render_template("/capture.html", error="Photo taken Successfully")
    else:
        return render_template("/capture.html", error = "Invalid Password")


@app.route("/take_photos", methods = ["POST", "GET"])

def retrieve_details(): 
    r = request
    u.add_user(r)
    return redirect(url_for("view_page"))

@app.route("/train", methods = ["POST", "GET"])

def train():
    print("[INFO] training Selected")
    print("[INFO] it might take long time to complete")
    ef.encode()
    return redirect(url_for("view_page"))
    




if __name__ == "__main__":
    app.run()


main()
