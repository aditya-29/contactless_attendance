import pandas as pd
import os
import numpy as np
import time
from datetime import date
import cv2
import utils as u
import xlsxwriter
# import threading
import time
import base64
from io import BytesIO
from imageio import imread

cap = None

today = date.today()
today = today.strftime("%d-%m-%Y")
print("[INFO] today's date: ",today)

xl_path = "../admin/users.xlsx"
auth_path = "../admin/auth.xlsx"
logs_dir = "../logs/"
logs_path = logs_dir + today + ".xlsx"


auth = pd.read_excel(auth_path)
try:
    logs = pd.read_excel(logs_path)
except:
    print("[INFO] logs file not initialised")


logs_col = ["s.no","id", "name", "category","entry_time", "exit_time"]

users_col = ["s.no", "id", "name", "category", "department", "age", "address line 1", "address line 2", 
		"city/village", "district", "state", "pin code", "S/o", "father's name", "mother's name", "nominee's name",
		"relationship to nominee", "educational qualifications", "previous work experience", "date of joining", "ESI",
		"PF", "mobile number", "alternate mobile number", "email id", "aadhar number", "pan number"]


def users_init():
    global xl
    df = pd.DataFrame(columns=users_col)
    # df.to_excel(xl_path, index=False)
    excel_save(df, xl_path)
    # time.sleep(1)
    xl = pd.read_excel(xl_path)

    print("sheet saved")


if os.path.exists(xl_path):
    pass
else:
    print("[INFO] users.xlsx created")
    users_init()

xl = pd.read_excel(xl_path)
xl_sno = list(xl["s.no"])
if xl_sno == []:
    xl_sno = 0
else:
    xl_sno = xl_sno[-1]


def auth_init():
    global auth

    df = pd.DataFrame(columns=["id", "name", "pwd"])
    # df.to_excel(auth_path, index=False)
    excel_save(df, auth_path)
    # time.sleep(1)
    auth = pd.read_excel(auth_path)

def map_col(col):
    global users_col

    dic = {users_col[0]:xl_sno}
    for i in range(len(col)):
        dic[users_col[i]] = col[i]
    return dic


def find_duplicates(sheet, id):
    if id in map(str,list(sheet["id"])):
        index = (sheet["id"] == id).index[0]
        return index
    else:
        return None



def add_user(r):
    global xl, xl_sno

    id = r.form["id"]
    id = str(id).upper()
    name = r.form["name"]
    cat = r.form["category"]
    department = r.form["department"]
    age = r.form["age"]

    add_line_1 = r.form["add line1"]
    add_line_2 = r.form["add line2"]
    add_city = r.form["add city/village"]
    add_district = r.form["add district"]
    add_state = r.form["add state"]
    add_pin = r.form["add pin"]

    so = r.form["s/o"]
    father = r.form["father's name"]
    mother = r.form["mother's name"]
    nominee = r.form["nominee's name"]
    nominee_rln = r.form["nominee's relationship"]

    edu_qual = r.form["edu quali"]
    prev_work = r.form["work exp"]
    doj = r.form["doj"]
    esi = r.form["esi"]
    pf = r.form["pf"]

    mob_no = r.form["mobile"]
    alt_mob_no = r.form["alternate mobile"]
    email = r.form["email"]
    aadhar = r.form["aadhar"]
    pan = r.form["pan"]

    xl_sno+=1

    col = [xl_sno, id,name,cat,department, age, add_line_1, add_line_2, add_city, add_district,
            add_state, add_pin, so, father, mother, nominee, nominee_rln, edu_qual, 
            prev_work, doj, esi, pf, mob_no, alt_mob_no, email, aadhar, pan]

    dic = map_col(col)

    res = find_duplicates(xl, id)

    if res == None:
        xl = xl.append(dic, ignore_index = True)
    else:
        xl.loc[res,1:] = col[1:]
    xl_sno = list(xl["s.no"])[-1]
    # xl.to_excel(xl_path, index = False)
    excel_save(xl, xl_path)
    # time.sleep(1)
    xl = pd.read_excel(xl_path) 

    print("sheet updated")

def authenticate(id, username, pwd):
    usernames = list(auth["name"])
    ids = list(auth["id"])
    pwds = list(auth["pwd"])

    usernames = list(map(str, usernames))
    ids = list(map(str, ids))
    pwds = list(map(str, pwds))

    print(usernames)
    print(ids)
    print(pwds)

    if id in ids:
        index = list(auth[auth["id"] == id].index)[-1]
        print(index)
        print("index : ",index)
        if usernames[index]==username and pwds[index] == pwd:
            print("authenticated")
            return True
    print("authenticaion error occured")
    return False

def logs_check():       #check for the availability of today's log file if not create one        
    global logs_path, logs_dir, today

    date = today

    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
        print("[INFO] directory created")

    if not os.path.exists(logs_dir + str(date) + ".xlsx"):
        print("[INFO] excel sheet not found")
        print("[INFO] creating excel sheet")

        logs_path = logs_dir + str(date) + ".xlsx"

        df = pd.DataFrame(columns=(logs_col))
        # df.to_excel(logs_path, index = False)
        excel_save(df, logs_path)
        # time.sleep(1)
        print("[INFO] excel sheet created")
    
    else:
        print("[INFO] excel sheet exists")
    return logs_path

def base64_to_cv(data):
    b64_string = data.decode()

    # reconstruct image as an numpy array
    img = imread(io.BytesIO(base64.b64decode(b64_string)))

    cv2_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return cv2_img


def excel_save(df, path):
    writer = pd.ExcelWriter(path, engine = "xlsxwriter")
    df.to_excel(writer, sheet_name = "sheet1", index = False)
    writer.save()
    writer.close()


def excel_download(filename):
    now = time.time()
    time.sleep(3)
    strIO = BytesIO()
    temp_df = pd.read_excel(filename)
    print(temp_df.head())
    excel_writer = pd.ExcelWriter(strIO, engine = "xlsxwriter")
    temp_df.to_excel(excel_writer, sheet_name = "sheet1")
    # time.sleep(1)
    excel_data = strIO.getvalue()
    strIO.seek(0)


    return strIO


if __name__ == "__main__":
    pass
