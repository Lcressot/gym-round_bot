import argparse
import logging
import sys
import numpy as np

import gym
from gym import wrappers
import matplotlib.pyplot as plt

import time

class RandomAgent(object):
    """The world's simplest agent!"""
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done):
        return self.action_space.sample()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-id','--env_id', default='RoundBot-v0', help='Select the environment to run')
    parser.add_argument('-sc','--step_count',  type=int,default=200, help='Number of steps in a trajectory')
    parser.add_argument('-w','--winsize', nargs=2, type=int, metavar=('w','h'), default=(16,16), help='Number of steps in a trajectory')
    parser.add_argument('-ep','--ep_count', type=int,default=25, help='number of episodes/trajetories')
    parser.add_argument('-r','--record', action="store_true", default=False, help='record to npz')
    parser.add_argument('-v','--verbose', action="store_true", default=False, help='verbose')
    parser.add_argument('--speed', type=float, default=1.0, help='agent\'s speed')
    parser.add_argument('--dteta', type=float, default=20.0, help='rotation angle')
    args = parser.parse_args()

    # read args from parsed command line
    episode_count = int(args.ep_count) #trajectories of size step_count
    step_count = int(args.step_count)
    winsize = args.winsize
    
    env = gym.make(args.env_id)    
    env.unwrapped.load(world='rb1',winsize=winsize, controller={"name":'Simple_TetaSpeed',"dteta":args.dteta,"speed":args.speed})
    agent = RandomAgent(env.action_space)

    reward = 0
    done = False
    
    if args.record:
        observations=np.zeros( [episode_count*step_count,winsize[0]*winsize[1]*3] )
        rewards=np.zeros(episode_count*step_count)
        actions=np.zeros([episode_count*step_count,1])
        episode_starts=np.zeros(episode_count*step_count,dtype=bool)
        
    for i in range(episode_count):
        ob = env.reset()
        t1= time.clock()
        t=0
        for j in range(step_count):
            action = agent.act(ob, reward, done)
            ob, reward, done, _ = env.step(action)
            if args.record:
                observations[i*step_count+j,:]=ob
                rewards[i*step_count+j]=reward
                actions[i*step_count+j]=action
            episode_starts[i*step_count+j]=(j==step_count-1)
            #env.render()
            t=t+1
        #plt.imshow(np.flipud(ob.reshape(16,16,3)),interpolation='nearest')
        #plt.pause(1)
        t2= time.clock()
        if args.verbose:
            print( "mean step time execution for trajectory "+str(i)+" : " + str((t2-t1)/t) )
             
            # Note there's no env.render() here. But the environment still can open window and
            # render if asked by env.monitor: it calls env.render('rgb_array') to record video.
            # Video is not recorded every episode, see capped_cubic_video_schedule for details.
    if args.record:
        #save dictionnary
        np.savez('./datarb1.npz', rewards=rewards, observations=observations, actions=actions,episode_starts=episode_starts)
    
    # Close the env and write monitor result info to disk
    env.close()
