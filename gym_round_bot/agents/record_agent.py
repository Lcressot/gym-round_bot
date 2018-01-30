import argparse
import logging
import sys
import numpy as np
import scipy.misc

import gym
from gym import wrappers
import matplotlib.pyplot as plt

import time

import agent

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-id','--env_id', default='CartPole-v0', help='Select the environment to run')
    parser.add_argument('-p','--policy_id', default='RandomAgent', help='Select the policy of the agent to run')
    parser.add_argument('-sc','--max_step_count',  type=int,default=200, help='Number of steps in a trajectory')
    parser.add_argument('-w','--winsize', nargs=2, type=int, metavar=('w','h'), default=(16,16), help='Number of steps in a trajectory')
    parser.add_argument('-ep','--ep_count', type=int,default=25, help='number of episodes/trajetories')
    parser.add_argument('-r','--record', action="store_true", default=False, help='record to npz')
    parser.add_argument('-v','--verbose', action="store_true", default=False, help='verbose')
    args = parser.parse_args()

    # read args from parsed command line
    episode_count = int(args.ep_count) #trajectories of size step_count
    max_step_count = int(args.max_step_count)

    
    env = gym.make(args.env_id)    
    policy=args.policy_id
    agent = agent.make(env.action_space,policy)
    
    reward = 0
    done = False
    
    env.reset()
    winsize=env.render(mode='rgb_array').shape
    new_winsize = args.winsize
    size_line=new_winsize[0]*new_winsize[1]*winsize[2]
    
    
    
    if args.record:
        observations=[]
        rewards=[]
        actions=[]
        episode_starts=[]
        
    for i in range(episode_count):
        ob = env.reset()
        t1= time.clock()
        t=0
        j=0
        done=False
        while not done:
            action = agent.act(ob, reward, done)
            ob, reward, done, _ = env.step(action)
            if not done:
                done = j>=max_step_count
            if args.record:
                rnd=env.render(mode='rgb_array')
                rnd=scipy.misc.imresize(rnd, (new_winsize[0],new_winsize[1],winsize[2]))
                observations.append(rnd.reshape((1,size_line)))
                rewards.append(reward)
                actions.append(action)
                episode_starts.append(done)
            j+=1
		
            #env.render()
            t=t+1
        #plt.imshow(np.flipud(ob.reshape(16,16,3)),interpolation='nearest')
        #plt.pause(1)
        t2= time.clock()
        if i==0:
            # print expected computation time
            print('expected computation time: '+str( (t2-t1)*episode_count) +' s') 
        if args.verbose:
            print( "mean step time execution for trajectory "+str(i)+" : " + str((t2-t1)/t) )
             
            # Note there's no env.render() here. But the environment still can open window and
            # render if asked by env.monitor: it calls env.render('rgb_array') to record video.
            # Video is not recorded every episode, see capped_cubic_video_schedule for details.
    if args.record:
        #save dictionnary
        observations=np.reshape(np.array(observations),(-1,size_line))
        observations=observations[:5000,:]
        rewards=np.array(rewards[:5000])
        actions=np.reshape(np.array(actions[:5000]),(-1,1))
        #episode_starts.insert(0,True)
        #episode_starts=episode_starts[:-1]
        episode_starts=np.zeros(5000,dtype=bool)
        episode_starts[0]=True
        episode_starts=np.array(episode_starts[:5000])
        np.savez('./datarb1.npz', rewards=rewards, observations=observations, actions=actions,episode_starts=episode_starts)
    
    # Close the env and write monitor result info to disk
    env.close()
