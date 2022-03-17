#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 15:58:56 2022

@author: Drew Tatum
"""

import numpy as np
import team_stats as TS
import time


##################### Notes
# An offensive rebound does not generate a new possesion in the stats field
# Field goal percentage needs to not take into consideration 3P%
# Need to look into distributions of variables 


class TeamSimulation(TS.ncaa_team_stats):
    def __init__(self):
        super().__init__()
        self.game_tracker = []
        self.n_simulations = 100000
        self.home_offense = []  
        self.home_defense = []
        self.away_offense = []  
        self.away_defense = []

        
    def get_parameters(self, ID1, ID2):  ################ use to get home and away stats (except pace) (can use both IDS at once or change so just one ID)
        ### Placeholder for getting actual stats
        self.home_offense = [5]  # Returning this in mean time
    
    def basketball_sim(self, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std):
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
        home_turnover_rate = .14
        home_two_shot_perc = .456
        home_three_shot_perc = .347
        home_three_shot_prob = (1083-435)/1083  # B/c sports reference doesn't have three % prob so calculated from other stats
        home_offense_rb_rate = .303
        # Away Stats
        away_turnover_rate = .18
        away_two_shot_perc = .400
        away_three_shot_perc = .318
        away_three_shot_prob = (1089-500)/1089
        away_offense_rb_rate = .300

        # Simulation 
        for game in range(self.n_simulations):
            home_score = 0
            away_score = 0
            poss_per_game = np.random.normal(np.mean([home_poss_mean, away_poss_mean]), np.mean([home_poss_std,  away_poss_std]))

            for shot in range(int(poss_per_game)):  # Each possession
                ### Home Team
                rebound_lost = False
                score = 0
                home_turnover = self.turnover_check(home_turnover_rate)  # Check for turnover
                if home_turnover == True:  # Offense turned over the ball
                    rebound_lost = True  
                while rebound_lost == False:  # Defense hasn't rebounded ball
                    score, rebound_lost = self.offense_sim(home_two_shot_perc, home_three_shot_perc, home_three_shot_prob, rebound_lost)  # Check if offense scores 
                    rebound_lost = self.rebound_check(home_offense_rb_rate, rebound_lost)  # Check if defense rebounds the ball
                home_score += score
                ### Away Team
                rebound_lost = False
                score = 0
                away_turnover = self.turnover_check(away_turnover_rate)  # Check for turnover
                if away_turnover == True:  # Offense turned over the ball
                    rebound_lost = True
                while rebound_lost == False:  # Defense hasn't rebounded ball
                    score, rebound_lost = self.offense_sim(away_two_shot_perc, away_three_shot_perc, away_three_shot_prob, rebound_lost)  # Check if offense scores 
                    rebound_lost = self.rebound_check(away_offense_rb_rate, rebound_lost)  # Check if defense rebounds the ball
                away_score += score           
  
            # Maybe add in free throws and defense stats
            self.game_tracker.append([home_score, away_score])
    
    def turnover_check(self, turnover_rate):
        turnover_val = False
        turnover = np.random.random()

        if turnover < turnover_rate:  # Check for turnover     
            turnover_val = True
        
        return turnover_val
    
    def offense_sim(self, two_shot_perc, three_shot_perc, three_shot_prob, rebound_lost):
        shot_attempt = np.random.random() # Shot probability
        shot_loc = np.random.random() # Check if shot is 3pt or 2pt
        score = 0  # Default
        if shot_loc < three_shot_prob:  # 3pt Shot
            if shot_attempt < three_shot_perc:
                score += 3 
        else:  # 2pt Shot
            if shot_attempt < two_shot_perc:
                score += 2 
        if score > 0:
            rebound_lost = True  # Basket made change of possession 

        return score, rebound_lost 
    
    def rebound_check(self, offense_rb_rate, rebound_lost):
        rebound_val = np.random.random()
        if rebound_val > offense_rb_rate:  # Defense secured rebound 
            rebound_lost = True
            
        return rebound_lost
    
    
    def defense_sim(self):
        
        return None 
    
    
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


start = time.time()
x = TeamSimulation()
x.get_parameters('ID1', 'ID2')
x.basketball_sim(team1_pace_mean=68, team1_pace_std=4, team2_pace_mean= 70, team2_pace_std=3)
x.sim_results()
print(x.win_percentage)
end = time.time()
print('Time it took: {:.2f}'.format(end-start))