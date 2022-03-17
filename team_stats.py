#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 09:42:08 2022

@author: Drew Tatum
"""

# Modules
import urllib
from bs4 import BeautifulSoup, SoupStrainer
import re
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
import json

class ncaa_team_stats:
    
    def __init__(self, year=2022):
        self.year = str(year)
        self.pace_mean = 0
        self.pace_std = 0
        self.bayesian = False
        self.historical_pace = []
        self.team_name = None
        self.team_ID = None
        self.team_dic = {}
        self.advanced_stats_dic = {}
        
    def compile_teams(self):
        """ """
        if len(self.team_dic) > 0:
            print('Team names already compiled')
            return 
        # Obtaining names of all teams for season for year given
        url = 'https://www.sports-reference.com/cbb/seasons/'+self.year+'-school-stats.html'
        
        # Obtain Team Names 
        url_loc = urllib.request.urlopen(url)
        url_html = url_loc.read()
        
        # Parsing URL
        strainer = SoupStrainer('a')
        soup = BeautifulSoup(url_html, 'html.parser', parse_only=strainer)

        # Obtaining Team Names For Year Given 
        team_pattern = re.compile('cbb/schools/(.*)/' + self.year)
        team_pattern2 = re.compile('>(.*)</a>')
        
        teams = {}
        for team in soup:
            team_name = re.findall(team_pattern, str(team))  # Used for url for team recent games
            if len(team_name) >= 1 and team_name[0] not in teams.keys():  
                team_name2 = re.findall(team_pattern2, str(team))
                if len(team_name2) >= 1: 
                    # Fix schools with &
                    team_name2[0] = team_name2[0].replace('&amp;', '&')
                    teams[team_name2[0]] = team_name[0]  # Adding the team name and its team url 
                    
        # Match team ID with team name using MTeamSpellings.csv file from https://www.kaggle.com/c/mens-march-mania-2022 
        try:
            infile = open('./MDataFiles_Stage1/MTeamSpellings.csv', 'r', encoding='cp1252')
        except FileNotFoundError:
            return './MDataFiles_Stage1/MTeamSpellings.csv path does not exist'
        self.team_spelling = {}
        for line in infile.readlines():
            new_line = line.strip().split(',')
            self.team_spelling[new_line[0]] = new_line[1]
        infile.close()

        # Creating a dictionary with team name as key with URL for each team and their name 
        self.team_dic = {}
        for key in teams.keys():
            val = teams[key]
            str_val = ''.join(filter(str.isalpha, key))
            for team_names in self.team_spelling.keys():
                str_team_name = ''.join(filter(str.isalpha, team_names))
                if val == team_names or key.lower() == team_names or str_val == str_team_name:
                    team_id = self.team_spelling[team_names]
                    self.team_dic[team_id] = {'URL': val, 'Name': key}
                    continue
        
    def obtain_team(self, ID):
        """Uses as input teamID from self.team_dic to obtain the game by game pace stats for a given year"""
        if len(self.team_dic) == 0:
            print('Need to run compile_teams first')
            return 
        
        # Obtaining game by game stats for team name given 
        self.team_ID = str(ID)
        self.team_name = self.team_dic[self.team_ID]['Name']
        team = self.team_dic[self.team_ID]['URL']
        team_url = 'https://www.sports-reference.com/cbb/schools/'+team+'/'+self.year+'-gamelogs-advanced.html'
        url_loc = urllib.request.urlopen(team_url)
        url_html = url_loc.read()
        strainer = SoupStrainer(id="div_sgl-advanced")
        soup = BeautifulSoup(url_html, 'html.parser', parse_only=strainer)
        
        # Obtain the pace per game from team's url game logs 
        pace_pattern = re.compile('"pace"\s*>(.*)<')
        if self.bayesian == False:
            self.pace_lst = []
        
        for item in soup.find_all(class_ = 'right'):
            pace_val = re.findall(pace_pattern, str(item))
            if len(pace_val) > 0:
                if self.bayesian == False:  # Default when running obtain_team method
                    try:
                        self.pace_lst.append(float(pace_val[0]))
                    except:
                        pass
                else:
                    self.historical_pace.append(float(pace_val[0]))
        # Mean and std of pace
        self.pace_mean = sum(self.pace_lst)/len(self.pace_lst)
        self.pace_std = np.std(self.pace_lst)
    
    def plot_pace(self):
        """Plots the Distribution of a Team's Pace"""
        if self.pace_mean == 0:
            print('Need to run obtain_team first')
            return
        
        sns.displot(self.pace_lst, bins = 15, kde = True, kind='hist')  # Most teams normalish distribution 
        plt.xlabel('Pace')
        plt.title(self.team_name + ' Pace Per Game')
        
    
    def bayesian_approach(self):
        """WORK IN PROGRESS"""
        if self.pace_mean == 0:  # Make sure have this year's data
            print('Run obtain_team first')
            return
        n_years = 2
        self.n_years = n_years
        self.current_pace = self.pace_lst
        self.historical_pace = []
        for year in range(self.n_years):
            self.bayesian = True
            self.year = str(int(self.year) - 1)  # Going back a year
            if self.year == '2021': # Not taking into consideration 2021 season b/c COVID and many teams didn't play
                self.n_years += 1
                self.year = str(int(self.year) - 1)
            self.obtain_team(self.team_ID)  # Obtain prior year pace
     
        # Set back to default 
        self.year = str(int(self.year) + self.n_years) 
        # Plot the pace of the historical data
        self.n_years = n_years
        self.plot_pace()
        self.bayesian = False
        
    def pace_file(self):
        """ Returns a dictionary with teamID as the key with the mean and std pace"""
        if len(self.team_dic) == 0:
            print('Need to run compile_teams first')
            return 
        
        self.pace_dic = {}
        for index, key in enumerate(self.team_dic.keys()):
            self.obtain_team(key)
            self.pace_dic[key] = {'Mean': self.pace_mean, 'Std': self.pace_std}
            #print(f'On team {index+1} out of {len(self.team_dic.keys())}')
            
        with open('./OutputData/pace_dic.json', 'w') as outfile:
            json.dump(self.pace_dic, outfile)
            
    def season_stats_file(self):
        """ Obtains the shooting stats and advanced stats for all teams. Returns a dictionary of the team stats with teamID as the key"""
        if len(self.team_dic) == 0 or len(self.advanced_stats_dic) ==0:
            print('Need to run compile_teams first and advanced_stats')
            return
        
        self.stat_dic = {}
        for index, key in enumerate(self.team_dic.keys()):
            two_point_percent, three_point_percent, ft_percent = self.shooting_stats(key)
            turnover = self.advanced_stats_dic[key]['Turnover%']
            FT_per_FG = self.advanced_stats_dic[key]['FT Per FG']
            ORB = self.advanced_stats_dic[key]['ORB%']
            three_per_fg = self.advanced_stats_dic[key]['Threes Per FG%']
    
            self.stat_dic[key] = {'2FG%': two_point_percent, '3FG%': three_point_percent, 'FT%': ft_percent, 
                                  'Turnover%': turnover, 'FT Per FG': FT_per_FG, 'ORB%':ORB, 'Threes Per FG%': three_per_fg}

        with open('./OutputData/season_stats_dic.json', 'w') as outfile:
            json.dump(self.stat_dic, outfile)
    
    def shooting_stats(self, ID):
        """Uses as input teamID from self.team_dic to obtain the two point, three point, and ft percentage of a given team for a given season"""
        if len(self.team_dic) == 0:
            print('Need to run compile_teams first')
            return 
        
        team_name = self.team_dic[ID]['URL']
        url = 'https://www.sports-reference.com/cbb/schools/' + team_name +'/'+self.year+'.html'
            
        # Obtain Team Names 
        url_loc = urllib.request.urlopen(url)
        url_html = url_loc.read()
        
        # Parsing URL
        strainer = SoupStrainer(id="schools_per_game")
        soup = BeautifulSoup(url_html, 'html.parser', parse_only=strainer)
        table = soup.find_all('tr')  # Team Stats 
        
        two_percentage_pattern = re.compile('fg2_pct">(.?\d*)<')
        three_percentage_pattern = re.compile('fg3_pct">(.?\d*)<')
        ft_percentage_pattern = re.compile('ft_pct">(.?\d*)<')
        
        two_percentage = float(re.findall(two_percentage_pattern, str(table[1]))[0])
        three_percentage = float(re.findall(three_percentage_pattern, str(table[1]))[0])
        ft_percentage = float(re.findall(ft_percentage_pattern, str(table[1]))[0])
        
        return two_percentage, three_percentage, ft_percentage

        
    def advanced_stats(self):
        """Obtains advanced stats for each team and returns advanced_stats_dic with the key as the teamID"""
        if len(self.team_dic) == 0:
            print('Need to run compile_teams first')
            return        
        
        url = 'https://www.sports-reference.com/cbb/seasons/'+self.year+'-advanced-school-stats.html'
            
        # Obtain Team Names 
        url_loc = urllib.request.urlopen(url)
        url_html = url_loc.read()
        
        # Parsing URL
        soup = BeautifulSoup(url_html, 'html.parser')
        table = soup.find_all('tr')
        
        # Patterns for Statistics 
        school_name = re.compile('schools/(.*)/'+self.year)
        turnover_rate_pattern = re.compile('tov_pct">(\d*?.?\d*)</td>')
        ft_rate_pattern = re.compile('ft_rate">(.\d*)</td>')
        orb_pattern = re.compile('orb_pct">(\d*?.?\d*?)</td>')
        three_per_fg_pattern = re.compile('fg3a_per_fga_pct">(.\d*)</td>')

        for row in table[2:]:
            team_name = re.findall(school_name, str(row))
            if len(team_name) >= 1:
                turnover_rate = re.findall(turnover_rate_pattern, str(row))[0]
                ft_rate = re.findall(ft_rate_pattern, str(row))[0]
                orb_rate = re.findall(orb_pattern, str(row))[0]
                three_per_fg_rate = re.findall(three_per_fg_pattern, str(row))[0]
                if team_name[0] in self.team_spelling.keys():  # Team Name matches spelling file
                    teamID = self.team_spelling[team_name[0]]
                    self.advanced_stats_dic[teamID] = {'Turnover%': turnover_rate, 'FT Per FG': ft_rate, 'ORB%': orb_rate, 'Threes Per FG%': three_per_fg_rate}
                else:  # Have to loop through team_dic to find the ID 
                    for key in self.team_dic.keys():
                            if team_name[0] == self.team_dic[key]['URL']:
                                teamID = key
                                self.advanced_stats_dic[teamID] = {'Turnover%': turnover_rate, 'FT Per FG': ft_rate, 'ORB%': orb_rate, 'Threes Per FG%': three_per_fg_rate}
        
        

#### Notes
# Limited in season stats, use Bayesian Inference approach
# Prior: Last n seasons of data
# Evidence: This season data 
