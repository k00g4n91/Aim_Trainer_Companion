import streamlit as st
import re
import difflib
import requests
import pandas as pd
import numpy as np
import steamleaderboards as sl
import zipfile
import matplotlib.pyplot as plt 
import matplotlib
import seaborn as sns 
import os
import shutil
from datetime import date
import csv
import time
import zipfile

#stats = pd.read_csv('F:\coding\Bootcamp\10\data\stats.csv')

#kovaaks_app_id = '824270'
#lbgroup = sl.LeaderboardGroup(kovaaks_app_id)
#scenario_names = stats['Scenario'].unique()


# TITLE
st.title("Kovaaks Aim Training Progress Tracker")
st.subheader('You\'re not as bad as you think... you\'re worse')

st.write("""##### Please navigate to your Steam folder.""")
st.write("""##### Go to this directory: 'Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer'.""")
st.write("""##### Right-click the '\stats' folder and 'Send to -> Compressed (zipped) folder'.""")
#user_github = st.text_input('Github Repository (to store your stats):')

st.session_state

temp = []

uploaded_zip = st.file_uploader("Upload your zipped stats folder", type="zip")
if (uploaded_zip is not None):
    with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
        zip_ref.extractall(temp)
    try:
        stats = pd.read_csv(temp + '\\stats.csv')
    except:
        stats = pd.DataFrame(columns=['Kills', 'Avg TTK', 'Score', 'Scenario'])

os.chmod()


# Create empty dict to store the 'target' data
data = {}
target = ['Kills:', 'Avg TTK:', 'Score:', 'Scenario:']

# Loop through
for filename in os.listdir(temp):
    f = open(f'{temp}/{filename}', 'r')
with f as csv_file:
    csv_reader = csv.reader(csv_file)
    for line in csv_reader:
        try:
            if line[0] in target:
                data[(line[0][:-1])] = line[1]     
        except IndexError:
            continue
    f.close()

ctime = time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(os.path.getmtime(f'{temp}/{filename}')))
data["Date"] = ctime
df = pd.DataFrame(data, index=[0]) 
stats = stats.append(df, ignore_index=True)    

                                
# CREATE A BUTTON FOR EACH UNIQUE SCENARIO NAME
#st.text_input('Which routine would you like to see:')

#all_scores = leaderboard_a.entries
#my_score = leaderboard_a.find_entry(MY_STEAMID_1)
#first_place_score = leaderboard_a.find_entry(rank=1)
#last_place_score = leaderboard_a.find_entry(rank=-1)









