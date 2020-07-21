import os
from flask import Flask, request, render_template, Response, url_for, redirect, flash, send_file, send_from_directory
import utils as u
from camera import Camera
from recognize_video import Camera as Camera_recog
import sys
import encode_faces as ef
import recognize_video as recog
import json
from time import localtime, strftime
from datetime import date
from io import BytesIO
import pandas as pd

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

upload_folder = "../logs/"
app.config["UPLOAD_FOLDER"] = upload_folder


app.config['DEBUG'] = True

str_res = None

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

@app.route("/login", methods = ["POST", "GET"])

def login():   #cross check the login information
    global pwd

    id = request.form["id"]
    id = str(id).upper()
    name = str(request.form["username"])
    pwd = str(request.form["password"])

    res = u.authenticate(id, name, pwd)
    if not res:
        flash('username / password incorrect')
        return render_template("index.html")
    else:
        path = u.logs_check()
        return redirect(url_for("attendance"))

@app.route("/logout", methods = ["POST", "GET"])

def logout():
    return render_template("index.html")


def gen_res():
    json_str = json.dumps(str_res)
    
    yield json_str


@app.route("/attendance_results", methods = ["POST", "GET"])
def attendance_results():
    temp = gen_res()
    return Response(temp, content_type="application/json")

@app.route("/attendance", methods = ["POST", "GET"])

def attendance():
    print("[INFO] attendance thread started")
    path = u.logs_check()

    # if str_res != None:
    #     flash([str_res["name"], str_res["id"], str_res["entry"], str_res["exit"],str_res["dup"]])
    return render_template("attendance.html")





@app.route("/register", methods = ["POST", "GET"])

def register():
    return render_template("register.html")

def gen(camera):
    global str_res
    while True:
        frame, str_res = camera.get_feed()
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
    temp_pwd = str(request.form["pwd"])

    if temp_pwd == pwd:
        recog.update_sheet(str(id))
        flash("registered successfully !")
        return redirect("attendance")

    else:
        flash("invalid username / password")
        return redirect("attendance")


@app.route('/video_feed')
def video_feed():
    # return ray.get(video_feed_thread.remote())
    print("[INFO] video feed thread started")
    camera = Camera()
    return Response(gen(camera),
        mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/video_feed_attendance")
def video_feed_attendance():
    global str_res
    print("[INFO] video feed thread started")
    camera_recog = Camera_recog()
    gen_res = gen(camera_recog)

    # print("-----res------", str_res)
    return Response(gen_res,
        mimetype='multipart/x-mixed-replace; boundary=frame')
    

@app.route("/save_pic", methods= ["POST", "GET"])
def capture():
    id = request.form["id"]
    id = str(id).upper()
    temp_pwd = str(request.form["pwd"])
    if temp_pwd == pwd:
        camera = Camera()
        stamp = camera.capture(id) 
        flash("photo saved")
        return render_template("/capture.html", error="green")
    else:
        flash("password incorrect")
        return render_template("/capture.html", error="#f44336")


@app.route("/take_photos", methods = ["POST", "GET"])

def retrieve_details(): 
    r = request
    u.add_user(r)
    flash("user added successfully")

    return redirect(url_for("register"))

@app.route("/train", methods = ["POST", "GET"])

def train():
    print("[INFO] training Selected")
    print("[INFO] it might take long time to complete")
    flash("Training started...")
    ef.encode()
    flash("Training completed !!!")
    return render_template("/capture.html", error="black")


@app.route("/download", methods = ["POST", "GET"])

def download():
    print("[INFO] downloading today's file")
    today = date.today()
    today = today.strftime("%d-%m-%Y")
    file_name   =  today +".xlsx"

    strIO = u.excel_download(app.config["UPLOAD_FOLDER"] + file_name)

    print("[INFO] filename : ", file_name)
    # print(app.config["UPLOAD_FOLDER"])

    full_name = app.config["UPLOAD_FOLDER"] + file_name

    # print("exists : ",os.path.exists(full_name))

    return send_file(full_name, attachment_filename = file_name, as_attachment=True, cache_timeout=0)



if __name__ == "__main__":
    app.run()


main()
