#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Merckling Astrid
    ISIR CNRS/UPMC
    2018

    Script for generating training data
    Generate n_ep*
""" 


import sys
import numpy as np
import argparse
import gym
import random
import math

from gym_round_bot.envs import round_bot_env
from gym_round_bot.envs import round_bot_controller


# path = os.path.abspath(__file__)
# dir_path = os.path.dirname(path)
# sys.path.insert(0, dir_path+'/../StaRep_RL/agents/')
sys.path.insert(0, '/home/astrid/Intel_Artif/2018/StaRep_RL/agents/')
from action_wrapper import ActionWrapper

parser = argparse.ArgumentParser(description='Training data options')

# Environment
parser.add_argument('--world', default='rb1', help='Select the world')
parser.add_argument('--texture', default='minecraft+', choices=['minecraft', 'minecraft+', 'colours'], help='Select the bricks texture')
parser.add_argument('--deterministic', action='store_true', default=False, help='Set a deterministic policy')
parser.add_argument('--controller', default='XZcontinuous', choices=['XZcontinuous','XZ', 'Theta', 'Theta2'], help='Select controller in Theta, Theta2, XZ')
parser.add_argument('--xztrange', nargs=2, type=int, default=(2, 2), help='xzrange and theta range')
parser.add_argument('--speed', type=float, default=10.0, help='agent\'s speed')
parser.add_argument('--dtheta', type=float, default=15.0, help='rotation angle')
parser.add_argument('--noise_ratio', type=float, default=0.0, help='Ratio of speed in additive gaussian noise stdv')
parser.add_argument('--max_step', type=int, default=200, help='Number of steps in a trajectory')

# Display options
parser.add_argument('--visible', action='store_true', default=True, help='See agent running in env')
parser.add_argument('--display', action='store_true', default=False, help='Display states\' representations')
parser.add_argument('--debug', action='store_true', default=False, help='Print positions, actions, rewards at each step for each env')
parser.add_argument('--winsize', nargs=2, type=int, metavar=('w', 'h'), default=None,
                    # default= None, default=[300,300],
                    help='Size of rendering window')
parser.add_argument('--obssize', nargs=2, type=int, metavar=('w', 'h'), default=(8, 8), help='Size of environment observations')#(16,16)
    
# Deterministic policies options
parser.add_argument('--nb_pi', type=int, default=32, help='number of policies')
parser.add_argument('--nb_trj', type=int, default=32, help='number of trajetories/policy')

args = parser.parse_args()

# create a controller given the command line argument :
if args.controller == 'XZcontinuous':
    controller = round_bot_controller.make(name='XZcontinuous', speed=args.speed, int_actions=False,
                                           xzrange=args.xztrange[0],noise_ratio = args.noise_ratio)  # recall 'int_actions=True' takes int actions

elif args.controller == 'XZ':
    controller = round_bot_controller.make(name='XZ', speed=args.speed, int_actions=False,
                                           xzrange=args.xztrange[0],noise_ratio = args.noise_ratio)  # recall 'int_actions=True' takes int actions
elif args.controller == 'Theta':
    controller = round_bot_controller.make(name='Theta', speed=args.speed, dtheta=args.dtheta, int_actions=False,
                                           xzrange=args.xztrange[0],
                                           thetarange=args.xztrange[1],noise_ratio = args.noise_ratio)  # recall 'int_actions=True' takes int actions
elif args.controller == 'Theta2':
    controller = round_bot_controller.make(name='Theta2', speed=args.speed, dtheta=args.dtheta, int_actions=False,
                                           xzrange=args.xztrange[0],
                                           thetarange=args.xztrange[1],noise_ratio = args.noise_ratio)  # recall 'int_actions=True' takes int actions


# set loading variables before creating env with make method
round_bot_env.set_metadata(
    world='rb1',
    obssize=(8,8),
    # winsize=(400,400),
    winsize=False,
    controller=controller,
    global_pov=None,
    visible=args.visible,
    perspective=True,
    multiview=False,
    focal=65.0,
    crash_stop=False,
    reward_stop=False,
    reward_count_stop=False,
    random_start=True,
    texture='minecraft+',
)

env = ActionWrapper(gym.make('RoundBot-v0'))

rewards = []
observations = []
image_lines = []
positions = []
actions = []
episode_starts = []


env.max_steps = args.max_step



for n_reset in range(args.nb_pi):
    env.reset()
    env.max_steps = args.max_step
    done = False
    # proportional–integral–derivative controller
    k_p = random.uniform(- 1.3, - 0.5)
    k_d = random.uniform(- 1.3, - 0.5)
    pos_d = np.array([random.uniform(-7.,7.), random.uniform(-7.,7.)])
    n_trj = 0

    observations_pi = []
    image_lines_pi = []
    rewards_pi = []
    actions_pi = []
    episode_starts_pi = []
    positions_pi = []


    while n_trj < args.nb_trj:

        observations_ep = []
        image_lines_ep = []
        rewards_ep = []
        actions_ep = []
        episode_starts_ep = []
        positions_ep = []

        done = False
        step = 0
        env.reset()
        # Can change initial velocity, default is : np.array([0, 0], dtype=float)
        # env.unwrapped._model.speed_continuous = np.array([0, 0], dtype=float)
        pos = np.array([env.unwrapped._model.robot_position[0], env.unwrapped._model.robot_position[2]])
        if args.debug:
            print("\nDesired Position : {}\n".format(pos_d))
            print("k_p : {}".format(k_p))
            print("k_d : {}\n".format(k_d))
            print("\npos : {}".format(pos))
        while not done:
            speed = env.unwrapped._model.speed_continuous
            action = k_p * (pos - pos_d) + k_d * speed
            if args.debug:
                print("\nact : {}".format(action))
                print("spe : {}".format(speed))
                print("____________________ {} ____________________".format(step))
            ob, reward, done, _ = env.step((action[0],action[1]))
            if args.debug:
                print("rew : {}".format(reward))

            pos = np.array([env.unwrapped._model.robot_position[0], env.unwrapped._model.robot_position[2]])
            if np.all(np.abs(pos - pos_d) < 5.e-1):
                done = True
            if (np.max(np.abs(pos))>8.):
                done = True
            if args.debug:
                print("done : {}".format(done))
                print("pos : {}\n".format(pos))
            # Convert RGB image to grayscale image : 0.2989 * R + 0.5870 * G + 0.1140 * B
            # ob = 0.2989 * ob[:, :, 0] + 0.5870 * ob[:, :, 1] + 0.1140 * ob[:, :, 2]
            # Normalization
            ob = ob / 255.
            img = ob.reshape([1, -1])

            observations_ep.append(ob)
            image_lines_ep.append(img)
            rewards_ep.append(reward)
            positions_ep.append(np.array(pos))
            actions_ep.append(action)
            episode_starts_ep.append(done)

            step += 1

        if (step > 8) & np.all(np.abs(pos - pos_d) < 5.e-1):
            # rewards.extend(rewards_ep)
            # observations.extend(observations_ep)
            # image_lines.extend(image_lines_ep)
            # positions.extend(positions_ep)
            # actions.extend(actions_ep)
            # episode_starts.extend(episode_starts_ep)

            rewards_pi.append(np.vstack(rewards_ep))
            observations_pi.append(np.array(observations_ep))
            image_lines_pi.append(np.vstack(image_lines_ep))
            positions_pi.append(np.vstack(positions_ep))
            actions_pi.append(np.vstack(actions_ep))
            episode_starts_pi.append(np.vstack(episode_starts_ep))

            n_trj = len(episode_starts_pi)

    rewards.append(np.vstack(rewards_pi))
    observations.append(np.vstack(observations_pi))
    image_lines.append(np.vstack(image_lines_pi))
    positions.append(np.vstack(positions_pi))
    actions.append(np.vstack(actions_pi))
    episode_starts.append(np.vstack(episode_starts_pi))

# episode_starts = np.vstack(episode_starts)
# observations = np.vstack(observations)
# image_lines = np.vstack(image_lines)
# positions = np.vstack(positions)
# rewards = np.vstack(rewards)
# actions=np.vstack(actions)
# episode_starts = np.vstack(episode_starts)
dict_viz = {"observations" : observations, "rewards" : rewards, "image_lines": image_lines,"positions": positions, "actions": actions, 'episode_starts':episode_starts}
np.savez( './data_viz_random_continuous.npz', **dict_viz )





















