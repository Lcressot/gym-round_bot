#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic & Merckling Astrid
    ISIR CNRS/UPMC
    02/2018

    Small script for testing and understanding the gym_round_bot environment
"""

import gym
import gym_round_bot

# create environment
import gym
import gym_round_bot
from gym_round_bot.envs import round_bot_env
from gym_round_bot.envs import round_bot_controller as rbc

# set variables 
world = 'rb1' # the world to load
obssize=[300,300] # the size of observations (rendering window)
winsize=[300,300] # the size of monitoring window (None if not wanted)

controller = rbc.make('XZ',speed=10,dtheta=15, xzrange=1, thetarange=1,noise_ratio=0.0) # the robot controller                
# set env metadata
round_bot_env.set_metadata(
        world=world,
        texture='minecraft+',
        obssize=obssize,
        winsize=winsize,
        controller=controller,
        normalize_rewards=False,
        position_observations=True,
        normalize_observations=True,
        observation_transformation = lambda X:X,
        distractors=True,
   )
# create env 
env = gym.make('RoundBot-v0')
# need to be called at least once
env.reset()  

# perform steps
while(True):
    ob, reward, done, _ = env.step(tuple(controller.action_space.sample()))
    # print(reward)
    # render to screen if needed
    env.render()
