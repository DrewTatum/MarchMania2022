#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 15:58:56 2022

@author: Drew Tatum
"""

import numpy as np
import team_stats as TS
import time
from TeamStatistics import TeamStatsForRegularSeason
from elo_rating import eloRating

##################### Notes
# An offensive rebound does not generate a new possesion in the stats field
# Field goal percentage needs to not take into consideration 3P%
# Need to look into distributions of variables 


class TeamSimulation(TS.ncaa_team_stats):
    def __init__(self, team1, team2):
        super().__init__()
        self.game_tracker = []
        self.n_simulations = 10000
        self.home_offense = []  
        self.home_defense = []
        self.away_offense = []  
        self.away_defense = []
        self.team1 = team1
        self.team2 = team2

        
    def get_parameters(self, ID1, ID2):  ################ use to get home and away stats (except pace) (can use both IDS at once or change so just one ID)
        ### Placeholder for getting actual stats
        self.home_offense = [5]  # Returning this in mean time
    
    def basketball_sim(self, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std):
        
        team1Stats = TeamStatsForRegularSeason(self.team1)
        team1Stats.fillInStats()
        team2Stats = TeamStatsForRegularSeason(self.team2)
        team2Stats.fillInStats()
        
        if len(self.home_offense) == 0:
            print('Run get_parameters first')
            return
        ### Team Stat Values
        self.game_tracker = []
        # Game Stats
        home_poss_mean = team1_pace_mean
        home_poss_std = team1_pace_std
        away_poss_mean = team2_pace_mean
        away_poss_std = team2_pace_std
        ### All these stats would be pulled by team ID just static for now
        # Home Stats
        home_turnover_rate = team1Stats.turnoverRate
        home_two_shot_perc = team1Stats.feildGoalPercentage
        home_three_shot_perc = team1Stats.threePointPercentage
        home_three_shot_prob = team1Stats.threePointShotsTaken  # B/c sports reference doesn't have three % prob so calculated from other stats
        home_offense_rb_rate = team1Stats.offensiveRebounds
        home_defense_rb_rate = team1Stats.defensiveRebounds

        # Away Stats/Team 2 Stats
        away_turnover_rate = team2Stats.turnoverRate
        away_two_shot_perc = team2Stats.feildGoalPercentage
        away_three_shot_perc = team2Stats.threePointPercentage
        away_three_shot_prob = team2Stats.threePointShotsTaken
        away_offense_rb_rate = team2Stats.offensiveRebounds
        away_defense_rb_rate = team2Stats.defensiveRebounds


        # Simulation 
        for game in range(self.n_simulations):
            home_score = 0
            away_score = 0
            poss_per_game = np.random.normal(np.mean([home_poss_mean, away_poss_mean]), np.mean([home_poss_std,  away_poss_std]))

            # Batch Home Team
            x = np.random.random(int(poss_per_game))
            poss_left = (x > home_turnover_rate).sum()  # Checks for turnovers
            while poss_left > 0:
                x = np.random.random(poss_left)
                three_point_attempt_count = (x < home_three_shot_prob).sum()
                three_shot = np.random.random(three_point_attempt_count)  # Num of three shot attempts
                two_shot = np.random.random(poss_left - len(three_shot))  # Num of two shot attempts
                three_made_num = (three_shot < home_three_shot_perc).sum()  # Made 3 pointer
                poss_left -= three_made_num
                two_made_num = (two_shot < home_two_shot_perc).sum()  # Made 2 pointer
                poss_left -= two_made_num
                home_score = home_score + (three_made_num * 3) + (two_made_num * 2)  # Update score
                rebound_x = np.random.random(poss_left)
                rebound_check = (rebound_x < away_defense_rb_rate).sum()  # Rebounds lost
                poss_left -= rebound_check
                
            #Batch Away Team
            x = np.random.random(int(poss_per_game))
            poss_left = (x > away_turnover_rate).sum()  # Checks for turnovers
            while poss_left > 0:
                x = np.random.random(poss_left)
                three_point_attempt_count = (x < away_three_shot_prob).sum()
                three_shot = np.random.random(three_point_attempt_count)  # Num of three shot attempts
                two_shot = np.random.random(poss_left - len(three_shot))  # Num of two shot attempts
                three_made_num = (three_shot < away_three_shot_perc).sum() # Made 3 pointer
                poss_left -= three_made_num
                two_made_num = (two_shot < away_two_shot_perc).sum() # Made 2 pointer
                poss_left -= two_made_num
                away_score = away_score + (three_made_num * 3) + (two_made_num * 2) # Update score
                rebound_x = np.random.random(poss_left)
                rebound_check = (rebound_x < home_defense_rb_rate).sum() # Rebounds lost
                poss_left -= rebound_check              
                
                if (poss_left*3 + away_score) < home_score:  # The away team can't catch up
                    poss_left = 0
            
            # Maybe add in free throws and defense stats
            self.game_tracker.append([home_score, away_score])
    
    
    def sim_results(self):
        home_win = 0
        tie_count = 0
        self.tot_sum = 0
        # Simulation results 
        for game_num in range(len(self.game_tracker)):
            if self.game_tracker[game_num][0] > self.game_tracker[game_num][1]:
                home_win += 1
            elif self.game_tracker[game_num][0] == self.game_tracker[game_num][1]:
                tie_count += 1
            self.tot_sum += self.game_tracker[game_num][0] + self.game_tracker[game_num][1]
        
        # Win Percentage
        self.win_percentage = home_win/(len(self.game_tracker)-tie_count)
        
    def elo_Probability(self):
        team1elo = eloRating(self.team1)
        team1elo.fillInStats()
        team2elo = eloRating(self.team2)
        team2elo.fillInStats()
        elo_diff_m = (team2elo.elo - team1elo.elo) / 400
        win_prob = 1 / (1+10**elo_diff_m)
        self.elo_win_percentage = win_prob
        
    def final_Prob(self):
        gs_prob = self.win_percentage
        elo_prob = self.elo_win_percentage
        elo_weight = .5
        stat_weight = 1-elo_weight
        win_prob_weighted = elo_prob/1*elo_weight + gs_prob/1*stat_weight
        self.weighted_win_percentage = win_prob_weighted

   
        

start = time.time()
x = TeamSimulation()
x.get_parameters('ID1', 'ID2')
x.basketball_sim(team1_pace_mean=68, team1_pace_std=4, team2_pace_mean= 70, team2_pace_std=3)
x.sim_results()
x.elo_Probability()
x.final_Prob()
#print(x.win_percentage)
print(x.weighted_win_percentage)
end = time.time()
print('Time it took: {:.2f}'.format(end-start))
# 100k simulations takes 29.98 seconds
# 100k simulations batched takes 18.56 seconds