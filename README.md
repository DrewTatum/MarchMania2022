# March Madness 2022

## Purpose
The purpose of this project is to use machine learning to predict the outcome of the March Madness 2022 tournament. 
Each teams win probability is calculated using two different approaches. The first method is a Monte Carlo simulation approach
based on offensive stats. This model will return the simulated win probability between two teams based on 100k 
simulations. Afterwards the second win probability is calculated using each teams Elo rating. A weighted scheme using
the win probability from both approaches is used to calculate the probability of team A beating team B. The output of 
this file was entered into <a href="https://www.kaggle.com/c/mens-march-mania-2022">Kaggle's 2022 March Mania Competition</a>. 
Since there are 68 teams at the beginning of the tournament, there are 2,278 potential matchups (!68/(2*!66)). 

