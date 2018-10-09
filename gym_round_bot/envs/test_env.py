#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018

    Small script for testing and understanding the gym_round_bot environment
"""

# create environment
import gym
import gym_round_bot
from gym_round_bot.envs import round_bot_env
from gym_round_bot.envs import round_bot_controller as rbc

# set variables 
world = {'name':'square','size':[20,20]} # the world to load
obssize=[300,300] # the size of observations (rendering window)
winsize=[600,600] # the size of monitoring window (None if not wanted)

controller = rbc.make('XZ',speed=1, speedrange=1, xzrange=[1,1], noise_ratio=0.0) # the robot controller                
# set env metadata
round_bot_env.set_metadata(
        world=world,
        texture='graffiti',
        obssize=obssize,
        winsize=winsize,
        controller=controller,
        normalize_rewards=False,
        position_observations=False,
        normalize_observations=True,
        observation_transformation = None,
        distractors=False,
        global_pov = (0,20,0)
   )
# create env 
env = gym.make('RoundBot-v0')
# need to be called at least once
env.reset()  
# perform steps
while(True):
    ob, reward, done, _ = env.step((tuple(controller.action_space.sample())))
    # render to screen if needed
    env.render()
