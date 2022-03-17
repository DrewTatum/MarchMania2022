#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 07:42:36 2022

@author: Drew Tatum
"""


import game_simulation_batch_jit as GS
import pandas as pd
#import json

# Pace mean and standard deviation for each team (Optimizes code by 2 minutes already having this file)
#with open('pace_dic.json', 'r') as infile:  # Requires running team_stats.pace_file previously 
#    pace_dic = json.load(infile)
        
# Calculating each potential matchup win probability
def main(year):
    ''' '''
    try:
        infile = open('./MDataFiles_Stage1/MNCAATourneySeeds.csv', 'r', encoding='cp1252')
        team_ids = []
        for line in infile.readlines():
            new_line = line.strip().split(',')
            if str(new_line[0]) == str(year):  # Look for the appropriate March Madness year
                team_ids.append(new_line[2])
    except FileNotFoundError:
        print('./MDataFiles_Stage1/MNCAATourneySeeds.csv path does not exist')
        return
    x = GS.TeamSimulation()
    x.year = str(year)
    x.compile_teams()  # Obtaining the pace for each team 
    x.pace_file()   # Can save about 2 mins exporting this file from team_stats (Will need to block this line and change team1 and team1 pace to remove the object 'x.')
    final_df = pd.DataFrame(columns=['ID1', 'ID2', 'Sim Pred', 'Elo Pred'])
    sorted_id = sorted(team_ids)  # Sorted 68 teams who made it to March Madness for the given year
    # Compare teams
    for spot, team1 in enumerate(sorted_id):
        for team2 in sorted_id[spot+1:]:
            # Pace for each team 
            team1_pace_mean = x.pace_dic[team1]['Mean']
            team1_pace_std = x.pace_dic[team1]['Std']
            team2_pace_mean = x.pace_dic[team2]['Mean']
            team2_pace_std = x.pace_dic[team2]['Std']
            ### Running Simulation
            x.run_sim(team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std) 
            x.sim_results()
            sim_win_prob = x.win_percentage
            ### Elo Win Probability
            x.elo_Probability()       
            elo_win_prob = x.elo_win_percentage
            # Adding results to dataframe
            final_df = final_df.append({'ID1': str(team1), 'ID2': str(team2), 'Sim Pred': sim_win_prob, 'Elo Pred': elo_win_prob}, ignore_index = True)
            
    return final_df

# Saving as cvs file
df = main(2019)
df.to_csv('win_probability.csv', index=False)



### Runtime is 9 mins for 1k batched simulations and 70 mins for 10k batched (Not ussing the pace_dic.json 2 min optimization)
### Runtime is 2.5 mins for 1k batched jit simulations and 4.5 mins for 10k batched jit and 25 mins for 100k batched jit 

### Above runtimes didn't include time to get individual team data (ran same team stats)
### 10k batched jit takes 10 mins to simulate wih all parts of the code