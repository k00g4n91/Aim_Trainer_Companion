import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import os
import shutil
from datetime import date
import csv
import time
import zipfile
import requests
import steam
from steam.steamid import SteamID
from steam.webapi import WebAPI, get
import steamleaderboards as sl
import os,sys,stat
from zipfile import ZipFile, ZipInfo
import difflib
import re
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit import stop
from functions import find_folder, search_hs_scenario, hs_timer, find_closest_match, make_graphs_png
from math import sin
import sys

dpg.create_context()

def dir_callback(sender, app_data):

    global dataDir

    dataDir = str((app_data.pop('file_path_name')))[1:]
    
    try:
        print('finding folder...')
        find_folder(dataDir)
        print('done')
    except Exception:
        print('Error')

def routine_callback(sender,app_data):

    global closest_match
    global stats
    global scenario_names
    global temp_df
    global high_score_df
    global current_hs

    if app_data:  
        print(f'user input: {app_data}')

        user_input = app_data
        stats = pd.read_csv('data/stats.csv')
        scenario_names = (stats['Scenario'].unique()).astype(str)
        closest_match = find_closest_match(stats,user_input)

        print(f'retrieving data for routine: {closest_match}')
        
        temp_df = stats.loc[stats['Scenario']==closest_match]

        search_hs_scenario(closest_match, stats, dataDir)

        high_score_df = pd.read_csv('data/high_score_df.csv')
        current_hs = max(high_score_df['Kill #'])

        print('routine retrieved')
        print(f'current high score :{current_hs}')
    else:
        print('no app_data')

def graph_callback(sender,app_data):
    if sender and closest_match:
        progress_graphs = make_graphs_png(temp_df,closest_match)
        with dpg.window(label="Progress Graphs", autosize=True):
            dpg.add_image('data/progress_graph.png',width=100,height=100)
            dpg.add_image('data/avg_progress_graph.png',width=100,height=100)

def timer_callback(sender,app_data):
    if sender:
        hs_timer(high_score_df)

def update_callback(sender,app_data):
    if sender:
        try:
            print('finding folder...')
            find_folder(dataDir)
            search_hs_scenario(closest_match, stats, dataDir)
            print('folder found')
            print(f'curent high score: {current_hs}')
        except Exception:
            print('Error')
    
dpg.add_file_dialog(show=False, callback=dir_callback, tag="file_dialog_id", default_filename= '')
dpg.create_viewport(title='Trackflix', width=800, height=500)
with dpg.window(label="Directory and Routine",autosize=True,tag='Primary Window'):
    dpg.add_text('PLEASE COMPLETE FIELDS IN ORDER!')
    dpg.add_spacer(height=10)
    dpg.add_text('When locating folder please click \'Drive\' and enter the FULL directory path into \'File Name\'')
    dpg.add_button(label="Locate stats folder", callback=lambda: dpg.show_item("file_dialog_id"))
    dpg.add_spacer(height=10)
    dpg.add_text('Type your desired routine and hit enter')
    dpg.add_input_text(label="Routine",callback=routine_callback,on_enter=True)
    dpg.add_spacer(height=10)
    dpg.add_button(label='See progress graphs',callback=graph_callback)
    dpg.add_spacer(height=10)
    dpg.add_button(label='Start timer',callback=timer_callback)
    dpg.add_spacer(height=10)
    dpg.add_button(label='Manual retrieve routine latest score',callback=update_callback)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()