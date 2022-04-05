#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 15:58:56 2022

@author: Drew Tatum
"""

import numpy as np
import team_stats as TS


##################### Notes
# An offensive rebound does not generate a new possesion in the stats field
# Field goal percentage needs to not take into consideration 3P%
# Need to look into distributions of variables


class TeamSimulation(TS.ncaa_team_stats):
    def __init__(self, n_simulations):
        super().__init__()
        self.game_tracker = []
        self.n_simulations = n_simulations
        self.home_offense = []
        self.home_defense = []
        self.away_offense = []
        self.away_defense = []

    def get_parameters(self, ID1,
                       ID2):  ################ use to get home and away stats (except pace) (can use both IDS at once or change so just one ID)
        ### Placeholder for getting actual stats
        self.home_offense = [5]  # Returning this in mean time

    def run_sim(self, team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std,
                team1_turnover_rate, team1_2shot_percent,
                team1_3shot_percent, team1_ft_percent, team1_3shot_prob, team1_orb_rate, team1_ft_per_fg,
                team2_turnover_rate, team2_2shot_percent,
                team2_3shot_percent, team2_ft_percent, team2_3shot_prob, team2_orb_rate, team2_ft_per_fg):

        ### Team Stat Values
        self.game_tracker = []
        # Game Stats
        home_poss_mean = team1_pace_mean
        home_poss_std = team1_pace_std
        away_poss_mean = team2_pace_mean
        away_poss_std = team2_pace_std

        # Home Stats/Team 1 Stats
        home_turnover_rate = float(team1_turnover_rate) / 100
        home_two_shot_perc = float(team1_2shot_percent)
        home_three_shot_perc = float(team1_3shot_percent)
        home_ft_perc = float(team1_ft_percent)
        home_three_shot_prob = float(team1_3shot_prob)
        home_offense_rb_rate = float(team1_orb_rate) / 100
        home_ft_per_fg = float(team1_ft_per_fg)

        # Away Stats/Team 2 Stats
        away_turnover_rate = float(team2_turnover_rate) / 100
        away_two_shot_perc = float(team2_2shot_percent)
        away_three_shot_perc = float(team2_3shot_percent)
        away_ft_perc = float(team2_ft_percent)
        away_three_shot_prob = float(team2_3shot_prob)
        away_offense_rb_rate = float(team2_orb_rate) / 100
        away_ft_per_fg = float(team2_ft_per_fg)

        # Simulation
        for game in range(self.n_simulations):
            home_score = 0
            away_score = 0
            poss_per_game = np.random.normal(np.mean([home_poss_mean, away_poss_mean]),
                                             np.mean([home_poss_std, away_poss_std]))

            for shot in range(int(poss_per_game)):  # Each possession
                ### Home Team
                rebound_lost = False
                score = 0
                home_turnover = self.turnover_check(home_turnover_rate)  # Check for turnover
                if home_turnover == True:  # Offense turned over the ball
                    rebound_lost = True
                while rebound_lost == False:  # Defense hasn't rebounded ball
                    score, rebound_lost = self.offense_sim(home_two_shot_perc, home_three_shot_perc,
                                                           home_three_shot_prob,
                                                           rebound_lost)  # Check if offense scores
                    rebound_lost = self.rebound_check(home_offense_rb_rate,
                                                      rebound_lost)  # Check if defense rebounds the ball
                home_score += score
                ### Away Team
                rebound_lost = False
                score = 0
                away_turnover = self.turnover_check(away_turnover_rate)  # Check for turnover
                if away_turnover == True:  # Offense turned over the ball
                    rebound_lost = True
                while rebound_lost == False:  # Defense hasn't rebounded ball
                    score, rebound_lost = self.offense_sim(away_two_shot_perc, away_three_shot_perc,
                                                           away_three_shot_prob,
                                                           rebound_lost)  # Check if offense scores
                    rebound_lost = self.rebound_check(away_offense_rb_rate,
                                                      rebound_lost)  # Check if defense rebounds the ball
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
        shot_attempt = np.random.random()  # Shot probability
        shot_loc = np.random.random()  # Check if shot is 3pt or 2pt
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
        self.win_percentage = home_win / (len(self.game_tracker) - tie_count)