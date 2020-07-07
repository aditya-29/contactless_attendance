import pandas as pd
import os
import numpy as np
import time

xl_path = "users.xlsx"
auth_path = "auth.xlsx"
logs_dir = "./logs/"

xl = pd.read_excel(xl_path)
auth = pd.read_excel(auth_path)
logs = pd.read_excel(logs_path)

def init():
    global xl
    df = pd.DataFrame(columns=["id", "name", "category"])
    df.to_excel(xl_path, index=False)
    xl = pd.read_excel(xl_path)

    print("sheet saved")

def auth_init():
    global auth

    df = pd.DataFrame(columns=["id", "name", "pwd"])
    df.to_excel(auth_path, index=False)
    auth = pd.read_excel(auth_path)

def add_user(name, id, cate):
    global xl

    dic = {"name": name, "id":id, "category": cate}
    xl = xl.append(dic, ignore_index = True)
    xl.to_excel(xl_path, index = False)
    xl = pd.read_excel(xl_path)

    print("sheet updated")

def authenticate(id, username, pwd):
    usernames = list(auth["name"])
    ids = list(auth["id"])
    pwds = list(auth["pwd"])

    if id in ids:
        index = (auth["id"] == id).index[0]
        if usernames[index]==username and pwds[index] == pwd:
            print("authenticated")
            return None
    print("authenticaion error occured")

def logs_init(date):
    if not os.path.exists(logs_path):
        os.create_dir

    if os.path.exits(logs_path + "_")



if __name__ == "__main__":
    authenticate(1001,"aditya", "qw")
