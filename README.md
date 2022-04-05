# March Madness 2022

## Purpose
The purpose of this project is to use machine learning to predict the outcome of the March Madness 2022 tournament. 
Each teams win probability is calculated using two different approaches. The first method is a Monte Carlo simulation approach
based on offensive stats. This model will return the simulated win probability between two teams based on 100k 
simulations. Afterwards the second win probability is calculated using each teams Elo rating. A weighted scheme using
the win probability from both approaches is used to calculate the probability of team A beating team B. The output of 
this file was entered into <a href="https://www.kaggle.com/c/mens-march-mania-2022">Kaggle's 2022 March Mania Competition</a>. 
Since there are 68 teams at the beginning of the tournament, there are 2,278 potential matchups. 

## Monte Carlo Model Parameters
The Monte Carlo Simulation is based only on the offensive parameters of each team. The stats that were used for each team 
were the following:
- Pace
- Turnover Rate
- Three Point Shot Probability (What fraction of total shots were three pointers)
- Two Point Shot Percentage
- Three Point Shot Percentage
- Offensive Rebound Rate

The number of simulations between two teams was defined as the number of games played between both of them. Therefore, 100k
simulations meant 100k games between the two teams. Since each team's pace is the number of possessions per 40 minutes, 
it was used as the model's parameter for the number of iterations through each game. Pace plays an import role in quantifying
a win. The intuition behind this logic is similar to the law of large numbers. Teams with a higher pace expect to play
closer to their "normal" performance, and we expect fewer outliers. The opposite can be considered for teams with a lower pace
value. When exploring each team's pace per game, there appeared to be a roughly normal distribution as seen below.

<p>
    <img src="./InputData/duke_pace.png"/>
    <img src="./InputData/virginia_pace.png"/>
</p>

During 

Three different models were created 

## Data

## Files

## Instructions 

## Runtime 
![Runtime Comparison](./OutputData/runtime.png)

The above plot looks at the time it takes to run N number of simulations between two teams using the three different
models created. Although the runtime will differ across systems, we can see the advantages using the JIT compilation 
model. When running 100k simulations each model had a mean win probability between the two teams within a 95% confidence
interval of each other. This validates that the models are performing similarly. Since the models are performing basically
the same, the JIT model is recommended since it takes drastically less computational time.

## Results
Overall the model performed decent within the competition finishing within the top 19% of all participants.


## Future Work
