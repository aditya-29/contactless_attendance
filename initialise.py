import pandas as pd
import os
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--date", required=True,
	help="enter the date to create the excel barebone file eg: 04_02_2020")
args = vars(ap.parse_args())    


date = args["date"]

df = pd.DataFrame(columns = ["s.no", "name", "id", "category", "entry_time", "exit_time"])

df.to_excel("logs/attendance_"+date+".xlsx")

print("file created..")