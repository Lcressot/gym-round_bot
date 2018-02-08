#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic & Merckling Astrid
    ISIR CNRS/UPMC
    02/2018
""" 

import numpy as np
import time
import copy
from collections import defaultdict
import scipy.misc
import random
from matplotlib import pyplot as plt


class Policy(object):
    """Policy for the agent"""
    def __init__(self, action_space):
        self.action_space=action_space
    def __call___(self,observation):
        raise Exception("not implemented error")


class Random_policy(Policy):
    def __init__(self,action_space):
        super(Random_policy,self).__init__(action_space)
    def __call__(self,observation):
        return self.action_space.sample()
 

class Greedy_policy(Policy):
    def __init__(self,action_space):
        super(Greedy_policy,self).__init__(action_space)
        self.Q = defaultdict(lambda: np.zeros(action_space.n))
    def __call__(self,observation):
        return np.argmax(self.Q[observation])


class Epsilon_greedy_policy(Greedy_policy):
    def __init__(self,action_space,epsilon):
        super(Epsilon_greedy_policy,self).__init__(action_space)
        self.epsilon=epsilon
    def __call__(self,observation,sample=True):
        """Makes probability vector of actions, and choose one randomly if sample"""
        if random.random() < self.epsilon:
            return super(Epsilon_greedy_policy,self).__call__(observation)
        else:
            return np.random.choice( xrange(self.action_space.n) )       


class Agent(object):
    """Simple agent with no update"""
    def __init__(self, action_space, policy, transformation=None):
        self.action_space = action_space
        self.policy=policy
        self.transformation=transformation#observation mapping to features

    def act(self, observation, reward, done, previous_action=None):
        action=self.policy(observation)

    def update(self,ob,new_ob,old_action,action,reward,done):
        """Default agent has not update"""
        return

    def train(self,env,n_ep,max_step,verbose=False,keep_screen=False,new_winsize=None):
        """Run n_ep episodes of maximum max_step length on environment env"""
        
        # init all used variables :
        reward = 0.0
        done = False
        screens=[]
        observations=[]
        rewards=[]
        actions=[]
        episode_starts=[]
        reward_ep=np.zeros((n_ep,1))
        seeds = env.seed(n_ep)
        t=0
        t1= time.time()   

        if keep_screen:
            env.reset()
            winsize=env.render(mode='rgb_array').shape

        for i in range(n_ep):
            # random seed to current time
            random.seed(seeds[i])
            ob = env.reset()
            if self.transformation:
                ob=self.transformation(ob)
            j=1
            done=False
            old_action=None
            while not done:
                # choose action from policy with current observation
                action = self.policy(ob)
                if type(action)!=type(int) and type(action)!=type(tuple()):
                    action=tuple(action) # convert lists to tuple for controller
                # perform a step in the environnment to observe the results of this action
                new_ob, reward, done, _ = env.step(action)
                if self.transformation:
                    new_ob=self.tranformation(new_ob)
                # update learning parameters accordingly
                self.update(ob,new_ob,old_action,action,reward,done)
                # stop if j is above max_step
                if not done:
                    done = j>=max_step
                # keep screens as line numpy arrays if asked
                if keep_screen:
                    rnd=env.render(mode='rgb_image')
                    if new_winsize:
                        rnd=scipy.misc.imresize(rnd, (new_winsize[0],new_winsize[1],3))                   
                    screens.append(rnd.reshape(-1))
                # keeps the rest of parameters for recording
                observations.append(ob)
                rewards.append(reward)
                actions.append(action)
                episode_starts.append(done)
                reward_ep[i]+=reward # rewards per episode
                # increase counters and save old variables
                j+=1
                ob=new_ob
                old_action=action                
                t+=1

                # print expected computation time
                if t==100:
                    t2= time.time()
                    print('Expected computation time: '+str( (t2-t1)/100.0*n_ep*max_step) +' s')

            if verbose:
                print( "mean step time execution for trajectory "+str(i)+" : " + str((t2-t1)/t) )
        t2= time.time()
        print('Final computation time: '+str(t2-t1) +' s')
        return {"reward_ep":reward_ep,"rewards":rewards, "observations":observations, "actions":actions, "episode_starts":episode_starts, "screens":screens}


class Agent_Q_learning(Agent):
    def __init__(self,action_space,policy, discount_factor=1.0, alpha=0.5, epsilon=0.1,transformation=None):
        super(Agent_Q_learning,self).__init__(action_space,policy,transformation)
        self.discount_factor = discount_factor
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self,ob,new_ob,old_action,action,reward,done): 
        td_delta = reward + self.discount_factor*np.max( self.policy.Q[new_ob])  - self.policy.Q[ob][action]
        self.policy.Q[ob][action] += self.alpha * td_delta
        