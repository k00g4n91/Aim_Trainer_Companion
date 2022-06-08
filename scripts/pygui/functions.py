import pandas as pd
import numpy as np
import os
import shutil
from datetime import date
import csv
import time
import zipfile
import os,sys,stat
import difflib
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

#find and clean data
def find_folder(dataDir):
  #dataDir = 'G:\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats'
  target = ['Kills:', 'Avg TTK:', 'Score:', 'Scenario:','Damage Done:']

  try:
      stats = pd.read_csv(dataDir + '\\stats.csv')
  except:
      stats = pd.DataFrame(columns=['Kills', 'Avg TTK', 'Score', 'Scenario','Damage Done'])

  # Empty dict to store our csv data
  data = {}

  # Go through all the files and store our target data in our empty dictionary, including the datetime of the file.
  for filename in os.listdir(dataDir):

      f = open(f'{dataDir}/{filename}', 'r')
      with f as csv_file:
          csv_reader = csv.reader(csv_file)
          for line in csv_reader:
              try:
                  if line[0] in target:
                      data[(line[0][:-1])] = line[1]     
              except IndexError:
                  continue
          f.close()

      scenario_date = f'{dataDir}/{filename}'[-29:-10]
      data["Date"] = scenario_date
      df = pd.DataFrame(data, index=[0])
      stats = pd.concat([stats,df]).drop_duplicates().reset_index(drop=True)

  stats['Kills'] = pd.to_numeric(stats['Kills'], downcast='integer')
  stats['Avg TTK'] = pd.to_numeric(stats['Avg TTK'], downcast='float')
  stats['Score'] = pd.to_numeric(stats['Score'], downcast='float')
  stats['Date'] = pd.to_datetime(stats['Date'], yearfirst=True, format=('%Y.%m.%d-%H.%M.%S'),exact=False)

  stats.to_csv("data/stats.csv", index=False)

#find the closest match to the user input routine
def find_closest_match(stats,user_input):

  scenario_names = (stats['Scenario'].unique()).astype(str)
  try:
      closest_match = (difflib.get_close_matches(str(user_input), scenario_names, n=1,cutoff=0.45).pop(0))
      return closest_match  
  except Exception:
      print('we can\'t find that scenario. Did u spel it rite?')

#search for your highest score
def search_hs_scenario(closest_match, stats, dataDir):

  #scenario_names = (stats['Scenario'].unique()).astype(str)

  #try:
  #    closest_match = (difflib.get_close_matches(str(user_input), scenario_names, n=1,cutoff=0.45).pop(0))
  #    print(closest_match)
  #except Exception:
  #    print('we can\'t find that scenario. Did u spel it rite?')
  #
  scenario = stats.loc[stats['Scenario'] == closest_match]

  high_score_date = []
# The following is simply to catch the high_score_date, nothing more!
  if sum(scenario['Score']) == 0.0:
      high_score_date.append(scenario.sort_values('Kills')['Date'].iloc[-1])
  elif sum(scenario['Kills']) > 0  and sum(scenario['Score']) > 0.0:
      high_score_date.append(scenario.sort_values('Score')['Date'].iloc[-1])

  hs_date = str(high_score_date[0])

  hs_year = hs_date[:4]
  hs_month = hs_date[5:7]
  hs_day = hs_date[8:10]
  hs_hour = hs_date[11:13]
  hs_min = hs_date[14:16]
  hs_sec = hs_date[17:19]

  Kill = []
  Time = []
  Acc = []
  Challenge_start = []

  for filename in os.listdir(dataDir):
      if f'{hs_year}.{hs_month}.{hs_day}-{hs_hour}.{hs_min}.{hs_sec} Stats.csv' in filename:
          f = open(f'{dataDir}/{filename}', 'r')
          with f as csv_file:
              csv_reader = csv.reader(csv_file)
              for line in csv_reader:
                  try:
                      Kill.append(line[0])
                      Time.append(line[1])
                      Acc.append(line[7])
                  except Exception:
                      break 
              for line in csv_reader:
                  try:
                      if line[0] in 'Challenge Start:' and line[1] not in 'H:M:S.s':
                          Challenge_start.append(line[1])
                      elif line[0] in 'Challenge Start:' and line[1] in 'H:M:S.s' or '':
                          start = pd.to_datetime(Time[-1]) - ((pd.to_datetime(Time[-1]) - pd.to_datetime(Time[1])).round(freq='T')) # deduce length between challenge start and first kill
                          Challenge_start.append(str(start)[11:-3])
                  except Exception:
                      continue              
          f.close()

  data_tuples = list(zip(Kill,Time,Acc))

  high_score_df = (pd.DataFrame(data_tuples,columns=('Kill #','Time', 'Accuracy'))
                      .replace(['Kill #','Accuracy'], 0)
                      ).replace('Timestamp',''.join(str(Challenge_start[0])))

  high_score_df['Kill #'] = pd.to_numeric(high_score_df['Kill #'], downcast='integer')
  high_score_df['Accuracy'] = pd.to_numeric(high_score_df['Accuracy'], downcast='float')
  high_score_df['Time'] = pd.to_datetime(high_score_df['Time'],format=('%H:%M:%S.%f'),exact=False)
  high_score_df['ms'] = (high_score_df['Time'] - high_score_df['Time'].iloc[0]) / pd.to_timedelta('1ms')

  high_score_df.to_csv('data/high_score_df.csv',index=False)

#graphs of your stats
def make_graphs_png(temp_df,closest_match):
    #temp_df = stats.loc[stats['Scenario']==closest_match]

    #GRAPH 1
    plt.rcParams["figure.figsize"] = (20,10)
    plt.xlabel('Date')
    plt.ylabel('Score/Kills')
    plt.title(f'{closest_match} Progress')
    plt.xticks(rotation=90)
    plt.grid(visible=True)
    plt.plot(temp_df['Date'], temp_df['Score'], color='green', marker='o', linestyle='solid',
         linewidth=2, markersize=2)
    plt.savefig('data/progress_graph.png')
    

    #GRAPH 2
    x = np.array(range(len(temp_df['Date']))).reshape((-1, 1))
    y = np.array(temp_df['Score']).reshape((-1, 1))
    plt.figure()
    plt.xlim(min(x), max(x))
    ax = sns.regplot(x=x,y=y)
    plt.xlabel('Days since started routine')
    plt.ylabel('Score/Kills')
    plt.title(f'{closest_match} AVG Progress')
    plt.grid(visible=True)
    plt.savefig('data/avg_progress_graph.png')
    
    plt.show()

    #TTK Graph
    slowest_ttk = max(temp_df['Avg TTK'])

    if slowest_ttk > 0:
        plt.rcParams["figure.figsize"] = (20,12)
        plt.xlabel('Date')
        plt.ylabel('Average_TTK in seconds')
        plt.title(f'{closest_match} AVG_TTK Progress')
        plt.xticks(rotation=90)
        plt.grid(visible=True)
        plt.plot(temp_df['Date'], temp_df['Avg TTK'], color='blue', marker='o', linestyle='solid',
            linewidth=2, markersize=2)
        plt.savefig('data/progress_graph.png')
        plt.show()

# line and linear regression of your progress
def prediction_graph(temp_df):
    temp_df['Days']= range(1,len(temp_df['Date'])+1)

    y = np.array(temp_df['Score']).reshape(-1, 1)
    X = np.array(temp_df['Days'])[:, np.newaxis]
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=.75, random_state=8)

    pr = LinearRegression()
    cubic = PolynomialFeatures(degree=3)
    X_cube = cubic.fit_transform(X)
    
    X_fit = np.arange(0, X.max()+7, 1)[:, np.newaxis]
    pr.fit(X_cube, y)
    y_cube_fit = pr.predict(cubic.fit_transform(X_fit))
    
    plt.figure(figsize=(20,10))
    plt.grid(which='both')
    plt.scatter(X, y)
    plt.plot(X_fit, y_cube_fit)
    plt.legend(loc='upper left')
    plt.savefig('data/prediction_graph.png')
    plt.show()

# replays your high score kill number and counts
# them up in realtime
def hs_timer(high_score_df):
    score_kills = 0

    for index, value in enumerate(high_score_df['ms']):
        if value == 0.0:
            print('3',end='\r')
            time.sleep(1.0)
            print('2',end='\r')
            time.sleep(1.0)
            print('1',end='\r')
            time.sleep(1.0)
            print('GO',end='\r')      
            time.sleep((high_score_df['ms'][1])/1000)
            score_kills += 1
            print(f'Score/Kills: {score_kills}',end='\r')
        else:
            try:
                if score_kills<max(high_score_df['Kill #']):
                    time.sleep((high_score_df['ms'][index+1] - high_score_df['ms'][index])/1000)
                    score_kills += 1 
                    print(f'Score/Kills: {score_kills}',end='\r')
                else:
                    print(f'finished! Current HighScore:{score_kills}',end='\r')
            except Exception:
                break

# shows you your percentage improvement since beginning the routine
def progress_stats(temp_df,closest_match):
    
    max_score = max(temp_df['Score'])
    lowest_score = min(temp_df['Score'])
    score_diff = max_score-lowest_score
    scor_percent_diff = round((score_diff/max_score)*100,2)
    slowest_ttk = max(temp_df['Avg TTK'])
    fastest_ttk = min(temp_df['Avg TTK'])
    ttk_diff = slowest_ttk - fastest_ttk

    if slowest_ttk > 0:
        ttk_percent_diff = round((ttk_diff/slowest_ttk)*100,2)
        print(f'{ttk_percent_diff}% or {ttk_diff} points improvement')
    else:
        print('Kovaaks did not provide any TTK information for this routine, try another')

    print(f'{score_diff} points or {scor_percent_diff}% between your lowest and highest scores')
