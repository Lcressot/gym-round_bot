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
obssize=[50,50] # the size of observations (rendering window)
winsize=[300,300] # the size of monitoring window (None if not wanted)

controller = rbc.make('Theta2',speed=5,dtheta=15, xzrange=1, thetarange=1) # the robot controller                
# set env metadata
round_bot_env.set_metadata(
        world=world,
        texture='minecraft',
        obssize=obssize,
        winsize=winsize,
        controller=controller,
   )
# create env 
env = gym.make('RoundBot-v0')

# create new controller, metadata and env
controller = rbc.make('Theta2',speed=5,dtheta=15, xzrange=1, thetarange=1) # the robot controller
round_bot_env.set_metadata(
        world=world,
        texture='colours',
        obssize=obssize,
        winsize=winsize,
        controller=controller,
   )
env2 = gym.make('RoundBot-v0')

# need to be called at least once
env.reset() 
env2.reset() 

# perform steps
while(True):
    ob, reward, done, _ = env.step((0,0)) # turn on itself
    ob, reward, done, _ = env2.step((1,0)) # turn and move
    # render to screen if needed
    env.render()
    env2.render()