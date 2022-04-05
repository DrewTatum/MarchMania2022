#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 21:24:31 2022

@author: Drew Tatum
"""

import game_simulation as gs_normal 
import game_simulation_batch as gs_batch
import game_simulation_batch_jit as gs_jit
import time 
import json 
import numpy as np
import seaborn as sns
import pandas as pd 
import matplotlib.pyplot as plt

### Compare Runtimes of Each Simulation File 

def main(n_simulations, n_iterations):
    ## Obtaining the Simulation Parameters 
    gs_sim_obj = gs_normal.TeamSimulation(n_simulations)
    gs_batch_obj = gs_batch.TeamSimulation(n_simulations)
    gs_jit_obj = gs_jit.TeamSimulation(n_simulations)
    # Using North Carolina and Kansas Team IDs
    north_carolina = str(1314)  # Will call NC
    kansas = str(1242)  # Will call K
    ## 
    try:
        with open('./OutputData/pace_dic.json', 'r') as infile:  # Requires running team_stats.pace_file previously
            pace_dic = json.load(infile)
        #
        with open('./OutputData/season_stats_dic.json', 'r') as infile:  # Requires running team_stats.season_stats_file previously
            season_stats = json.load(infile)    
    except:
        print("./OutputData/season_stats_dic.json or ./OutputData/pace_dic.json doesn't exist")
        print("Run team_stats.py file to obtain both json files")
        return 
    # Assigning Team Stats
    team1 = north_carolina
    team2 = kansas 
    # North Carolina Stats 
    team1_turnover_rate = season_stats[team1]['Turnover%']
    team1_2shot_percent = season_stats[team1]['2FG%']
    team1_3shot_percent = season_stats[team1]['3FG%']
    team1_ft_percent = season_stats[team1]['FT%']
    team1_3shot_prob = season_stats[team1]['Threes Per FG%']
    team1_orb_rate = season_stats[team1]['ORB%']
    team1_ft_per_fg = season_stats[team1]['FT Per FG']
    team1_pace_mean = pace_dic[team1]['Mean']
    team1_pace_std = pace_dic[team1]['Std']
    team2_pace_mean = pace_dic[team2]['Mean']
    team2_pace_std = pace_dic[team2]['Std']
    # Kansas Stats 
    team2_turnover_rate = season_stats[team2]['Turnover%']
    team2_2shot_percent = season_stats[team2]['2FG%']
    team2_3shot_percent = season_stats[team2]['3FG%']
    team2_ft_percent = season_stats[team2]['FT%']
    team2_3shot_prob = season_stats[team2]['Threes Per FG%']
    team2_orb_rate = season_stats[team2]['ORB%']
    team2_ft_per_fg = season_stats[team2]['FT Per FG']
    
    iterations = n_iterations 
    
    # Normal Game Simulation
    gs_normal_lst = []
    for i in range(iterations):
        start = time.time()
        gs_sim_obj.run_sim(team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std, team1_turnover_rate, team1_2shot_percent,
            team1_3shot_percent, team1_ft_percent, team1_3shot_prob, team1_orb_rate, team1_ft_per_fg, team2_turnover_rate, team2_2shot_percent,
            team2_3shot_percent, team2_ft_percent, team2_3shot_prob, team2_orb_rate, team2_ft_per_fg) 
        
        end = time.time()
        gs_normal_lst.append(end-start)
    
    # Batch Game Simulation 
    gs_batch_lst = []
    for i in range(iterations):
        start = time.time()
        gs_batch_obj.run_sim(team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std, team1_turnover_rate, team1_2shot_percent,
            team1_3shot_percent, team1_ft_percent, team1_3shot_prob, team1_orb_rate, team1_ft_per_fg, team2_turnover_rate, team2_2shot_percent,
            team2_3shot_percent, team2_ft_percent, team2_3shot_prob, team2_orb_rate, team2_ft_per_fg) 
        
        end = time.time()
        gs_batch_lst.append(end-start)
    
    # JIT Batch Game Simulation 
    gs_jit_lst = []
    for i in range(iterations):
        start = time.time()
        gs_jit_obj.run_sim(team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std, team1_turnover_rate, team1_2shot_percent,
            team1_3shot_percent, team1_ft_percent, team1_3shot_prob, team1_orb_rate, team1_ft_per_fg, team2_turnover_rate, team2_2shot_percent,
            team2_3shot_percent, team2_ft_percent, team2_3shot_prob, team2_orb_rate, team2_ft_per_fg) 
        
        end = time.time()
        gs_jit_lst.append(end-start)
        
    
    return np.mean(gs_normal_lst), np.mean(gs_batch_lst), np.mean(gs_jit_lst)
    
    

simulation_lst = [1, 1000, 5000, 10000, 50000]
df = pd.DataFrame(columns = ['Sim Number', 'Normal Time', 'Batch Time', 'Jit Time'])

for sim_num in simulation_lst:
    gs_normal_time, gs_batch_time, gs_jit_time = main(sim_num, n_iterations=3)
    # Pandas DataFrame of Results 
    if sim_num == 1:  # JIT compilation slower first run
        continue
    new_row = {'Sim Number': sim_num, 'Normal Time': round(gs_normal_time,3), 'Batch Time': round(gs_batch_time,3), 'Jit Time': round(gs_jit_time,3)}
    df = df.append(new_row, ignore_index=True)

# Plotting
df = df.astype({'Sim Number': 'int32'})
df_revised = df.melt('Sim Number', var_name='Sim Type', value_name='Time')
 

ax = sns.barplot(data = df_revised, x ='Sim Number', y = 'Time', hue='Sim Type')
try:
    for container in ax.containers:
        ax.bar_label(container)
except:
    print('Requires Matplotlib 3.4 for displaying values on graph')
    
plt.title('Program Runtime per Simulation Count')
plt.xlabel('Number of Simulations')
plt.ylabel('Time (Seconds)')
plt.savefig('./OutputData/runtime.png')
plt.show()
