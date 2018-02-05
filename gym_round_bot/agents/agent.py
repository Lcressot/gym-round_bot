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

        # nA=self.action_space.n
        # action_probs = np.ones(nA, dtype=float) * self.epsilon / nA
        # action_probs[best_action] += (1.0 - self.epsilon)
        # if not sample:
        #     return action_probs
        # else:
        #     return np.random.choice(np.arange(len(action_probs)), p=action_probs)


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
        reward = 0.0
        done = False
        screens=[]
        observations=[]
        rewards=[]
        actions=[]
        episode_starts=[]
        reward_ep=np.zeros((n_ep,1))
        t=0
        t1= time.clock()   

        if keep_screen:
            env.reset()
            winsize=env.render(mode='rgb_array').shape
            size_line=new_winsize[0]*new_winsize[1]*3

        for i in range(n_ep):
            # random seed to current time
            random.seed(None)
            ob = env.reset()
            if self.transformation:
                ob=self.transformation(ob)
            j=1
            done=False
            old_action=None
            while not done:
                action = self.policy(ob)
                new_ob, reward, done, _ = env.step(action)
                if self.transformation:
                    new_ob=self.tranformation(new_ob)
                self.update(ob,new_ob,old_action,action,reward,done)
                if not done:
                    done = j>=max_step
                if keep_screen:
                    rnd=env.render(mode='rgb_image')
                    #rnd=scipy.misc.imresize(rnd, (new_winsize[0],new_winsize[1],3))
                    #plt.imshow(rnd.reshape(16,16,3), interpolation='nearest')
                    #plt.imshow(rnd)
                    #plt.pause(0.0001)
                    #rnd=rnd.reshape((new_winsize[0],new_winsize[1],3))/255.
                    screens.append(rnd.reshape(-1))
                observations.append(ob)
                rewards.append(reward)
                actions.append(action)
                episode_starts.append(done)
                j+=1
                ob=new_ob
                old_action=action
                reward_ep[i]+=reward
                t+=1
                if t==100:
                    # print expected computation time
                    t2= time.clock()
                    print('Expected computation time: '+str( (t2-t1)/100.0*n_ep*max_step) +' s')
            if verbose:
                print( "mean step time execution for trajectory "+str(i)+" : " + str((t2-t1)/t) )
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
        #print(self.policy.Q[ob])
#class RandomAgent(Agent):
#    """The world's simplest agent!"""
#    def __init__(self, action_space):
#        super(RandomAgent,self).__init__(action_space)
#
#    def act(self, observation, reward, done):
#        return self.action_space.sample()
#
#class GreedyAgent(Agent):
#    """The world's simplest agent!"""
#    def __init__(self, action_space):
#        super(GreedyAgent,self).__init__(action_space)
#
#    def act(self, observation, reward, done,Q):
#
#        return self.action_space.sample()
#
#def make(action_space,policy='RandomAgent',info={}):
#    if policy=='RandomAgent':
#   return RandomAgent(action_space)
#    elif policy=='GreedyAgent':
#   return GreedyAgent(action_space)
#    else:
#   raise Exception("Unknown policy in agent.make: " +policy)
