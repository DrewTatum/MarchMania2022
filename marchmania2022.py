#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 07:42:36 2022

@author: Drew Tatum
"""

import game_simulation_batch_jit as GS
import pandas as pd
import json

# Can Optimize Runtime with following two dictionaries preloaded (Won't need x.pace_file, x.advanced_stats or x.season_stats_file)
with open('./OutputData/pace_dic.json', 'r') as infile:  # Requires running team_stats.pace_file previously
    pace_dic = json.load(infile)
#
with open('./outputData/season_stats_dic.json', 'r') as infile:  # Requires running team_stats.season_stats_file previously
    season_stats = json.load(infile)


# Elo Ratings From (https://www.warrennolan.com/basketball/2022/elo)
df = pd.read_csv('./InputData/elo_2022.csv')
elo_dic = {}
for index, key in enumerate(df.TeamID):
    elo_dic[key] = df.ELO[index]
        
# Calculating each potential matchup win probability
def main(year):
    ''' '''
    try:
        infile = open('./MDataFiles_Stage2/MNCAATourneySeeds.csv', 'r', encoding='cp1252')
        team_ids = []
        for line in infile.readlines():
            new_line = line.strip().split(',')
            if str(new_line[0]) == str(year):  # Look for the appropriate March Madness year
                team_ids.append(new_line[2])
    except FileNotFoundError:
        print('./MDataFiles_Stage2/MNCAATourneySeeds.csv path does not exist')
        return
    x = GS.TeamSimulation()
    x.year = str(year)
    x.compile_teams()  # Obtaining the pace for each team 
    #x.pace_file()   # Can comment out these 5 lines if reading in both json files
    #x.advanced_stats()  # Can comment out these 5 lines if reading in both json files
    #x.season_stats_file()  # Can comment out these 5 lines if reading in both json files
    #season_stats = x.stat_dic  # Can comment out these 5 lines if reading in both json files
    #pace_dic = x.pace_dic  # Can comment out these 5 lines if reading in both json files
    final_df = pd.DataFrame(columns=['ID', 'Pred'])
    bracket_df = pd.DataFrame(columns=['ID1', 'ID2', 'Sim Pred', 'Elo Pred'])
    sorted_id = sorted(team_ids)  # Sorted 68 teams who made it to March Madness for the given year
    # Compare teams
    for spot, team1 in enumerate(sorted_id):
        # Team1 Stats
        team1_turnover_rate = season_stats[team1]['Turnover%']
        team1_2shot_percent = season_stats[team1]['2FG%']
        team1_3shot_percent = season_stats[team1]['3FG%']
        team1_ft_percent = season_stats[team1]['FT%']
        team1_3shot_prob = season_stats[team1]['Threes Per FG%']
        team1_orb_rate = season_stats[team1]['ORB%']
        team1_ft_per_fg = season_stats[team1]['FT Per FG']
        for team2 in sorted_id[spot+1:]:
            # Pace for each team 
            team1_pace_mean = pace_dic[team1]['Mean']
            team1_pace_std = pace_dic[team1]['Std']
            team2_pace_mean = pace_dic[team2]['Mean']
            team2_pace_std = pace_dic[team2]['Std']
            # Team2 Stats
            team2_turnover_rate = season_stats[team2]['Turnover%']
            team2_2shot_percent = season_stats[team2]['2FG%']
            team2_3shot_percent = season_stats[team2]['3FG%']
            team2_ft_percent = season_stats[team2]['FT%']
            team2_3shot_prob = season_stats[team2]['Threes Per FG%']
            team2_orb_rate = season_stats[team2]['ORB%']
            team2_ft_per_fg = season_stats[team2]['FT Per FG']
            ### Running Simulation
            x.run_sim(team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std, team1_turnover_rate, team1_2shot_percent,
                team1_3shot_percent, team1_ft_percent, team1_3shot_prob, team1_orb_rate, team1_ft_per_fg, team2_turnover_rate, team2_2shot_percent,
                team2_3shot_percent, team2_ft_percent, team2_3shot_prob, team2_orb_rate, team2_ft_per_fg) 
            x.sim_results()
            sim_win_prob = x.win_percentage
            ### Elo Win Probability
            team1elo = elo_dic[int(team1)]
            team2elo = elo_dic[int(team2)]
            x.elo_Probability(team1elo, team2elo)       
            elo_win_prob = x.elo_win_percentage
            ### Combined Win Probability From 2019 Testing
            combined_win_prob = .7 * elo_win_prob + .3 * sim_win_prob
            # Adding results to dataframe
            final_df = final_df.append({'ID': str(year)+'_'+str(team1)+'_'+str(team2), 'Pred': combined_win_prob}, ignore_index = True)
            bracket_df = bracket_df.append({'ID1': str(team1), 'ID2': str(team2), 'Sim Pred': sim_win_prob, 'Elo Pred': elo_win_prob}, ignore_index = True)

            
    return final_df, bracket_df

# Saving as cvs file
df, bracket_df = main(2022)
df.to_csv('./OutputData/kaggle_win_probability.csv', index=False)
bracket_df.to_csv('./OutputData/win_probability.csv', index=False)



### Runtime is 9 mins for 1k batched simulations and 70 mins for 10k batched (Not ussing the pace_dic.json 2 min optimization)
### Runtime is 2.5 mins for 1k batched jit simulations and 4.5 mins for 10k batched jit and 25 mins for 100k batched jit 

### Above runtimes didn't include time to get individual team data (ran same team stats)
### 10k batched jit takes 10 mins to simulate wih all parts of the code