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

    def run_sim(self, team1, team2, team1_pace_mean, team1_pace_std, team2_pace_mean, team2_pace_std,
                team1_turnover_rate, team1_2shot_percent,
                team1_3shot_percent, team1_ft_percent, team1_3shot_prob, team1_orb_rate, team1_ft_per_fg,
                team2_turnover_rate, team2_2shot_percent,
                team2_3shot_percent, team2_ft_percent, team2_3shot_prob, team2_orb_rate, team2_ft_per_fg):
        self.game_tracker = []
        self.team1 = team1
        self.team2 = team2

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

        # Possession Mean and Std for the normal distribution random numbers
        mean_poss = np.mean([home_poss_mean, away_poss_mean])
        std_poss = np.mean([home_poss_std, away_poss_std])

        # Simulation
        for game in range(self.n_simulations):
            home_score = 0
            away_score = 0
            poss_per_game = np.random.normal(mean_poss, std_poss)

            # Batch Home Team (Team1)
            x = np.random.random(int(poss_per_game))
            poss_left = (x > home_turnover_rate).sum()  # Checks for turnovers

            while poss_left > 0:
                shots = np.random.random(poss_left)
                three_point_attempt_count = (shots < home_three_shot_prob).sum()
                three_shot = np.random.random(three_point_attempt_count)  # Num of three shot attempts
                two_shot = np.random.random(poss_left - len(three_shot))  # Num of two shot attempts
                three_made_num = (three_shot < home_three_shot_perc).sum()  # Made 3 pointer
                poss_left -= three_made_num
                two_made_num = (two_shot < home_two_shot_perc).sum()  # Made 2 pointer
                poss_left -= two_made_num
                home_score = home_score + (three_made_num * 3) + (two_made_num * 2)  # Update score
                rebound_x = np.random.random(poss_left)
                rebound_check = (rebound_x > home_offense_rb_rate).sum()  # Rebounds lost
                poss_left -= rebound_check

            # Batch Away Team (Team2)
            x = np.random.random(int(poss_per_game))
            poss_left = (x > away_turnover_rate).sum()  # Checks for turnovers
            while poss_left > 0:
                shots = np.random.random(poss_left)
                three_point_attempt_count = (shots < away_three_shot_prob).sum()
                three_shot = np.random.random(three_point_attempt_count)  # Num of three shot attempts
                two_shot = np.random.random(poss_left - len(three_shot))  # Num of two shot attempts
                three_made_num = (three_shot < away_three_shot_perc).sum()  # Made 3 pointer
                poss_left -= three_made_num
                two_made_num = (two_shot < away_two_shot_perc).sum()  # Made 2 pointer
                poss_left -= two_made_num
                away_score = away_score + (three_made_num * 3) + (two_made_num * 2)  # Update score
                rebound_x = np.random.random(poss_left)
                rebound_check = (rebound_x > away_offense_rb_rate).sum()  # Rebounds lost
                poss_left -= rebound_check

                if (
                        poss_left * 3 + away_score) < home_score:  # The away team can't catch up (Only since care about win probability not score)
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
        self.win_percentage = home_win / (len(self.game_tracker) - tie_count)

    def elo_Probability(self, team1elo, team2elo):
        elo_diff = (team2elo - team1elo) / 400
        win_prob = 1 / (1 + 10 ** elo_diff)
        self.elo_win_percentage = win_prob  # Of team 1 winning

    def final_Prob(self):
        gs_prob = self.win_percentage
        elo_prob = self.elo_win_percentage
        elo_weight = .5
        stat_weight = 1 - elo_weight
        win_prob_weighted = elo_prob / 1 * elo_weight + gs_prob / 1 * stat_weight
        self.weighted_win_percentage = win_prob_weighted
