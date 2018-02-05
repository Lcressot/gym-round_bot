import argparse
import logging
import sys
import numpy as np
import gym
from gym import wrappers
import matplotlib.pyplot as plt
import time
import agent


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-id','--env_id', default='RoundBot-v0', help='Select the environment to run')
    parser.add_argument('-p','--policy_id', default='RandomAgent', help='Select the policy of the agent to run')
    parser.add_argument('-ms','--max_step',  type=int,default=200, help='Number of steps in a trajectory')
    parser.add_argument('-w','--winsize', nargs=2, type=int, metavar=('w','h'), default=(16,16), help='Number of steps in a trajectory')
    parser.add_argument('-ep','--n_ep', type=int,default=26, help='number of episodes/trajetories')
    parser.add_argument('-r','--recordto', default='./datarb1.npz', help='npz record file')
    parser.add_argument('-v','--verbose', action="store_true", default=False, help='verbose')
    parser.add_argument('--speed', type=float, default=10.0, help='agent\'s speed')
    parser.add_argument('--dtheta', type=float, default=20.0, help='rotation angle')
    args = parser.parse_args()

    if not '.npz' in args.recordto:
        raise Exception('option recordto is not npz')

    # read args from parsed command line
    n_ep = int(args.n_ep) #trajectories of size max_step
    max_step = int(args.max_step)
    winsize = args.winsize
    
    env = gym.make(args.env_id)
    if args.env_id=='RoundBot-v0':
       env.unwrapped.load(world='rb1',winsize=winsize, controller={"name":'Simple_XZ',"speed":args.speed,"xzrange":2},global_pov=(0,20,0),perspective=False)
       env.action_space = env.unwrapped.action_space
    #policy=args.policy_id
    #myagent = myagent.make(env.action_space,policy)
    
    policy=agent.Random_policy(env.action_space)
    # policy=agent.Epsilon_greedy_policy(env.action_space,epsilon=0.1)
    # myagent=agent.Agent_Q_learning(env.action_space,policy)
    myagent=agent.Agent(env.action_space,policy)
    stats=myagent.train(env,n_ep,max_step,verbose=False,keep_screen=True,new_winsize=(16,16,3))
    # plt.plot(stats["reward_ep"])
    # plt.show()

    #policy2=agent.Greedy_policy(env.action_space)
    #policy2.Q = policy.Q
    #myagent.policy=policy2
    #myagent=agent.Agent(env.action_space,policy)
    #stats=myagent.train(env,n_ep,max_step,verbose=False,keep_screen=False,new_winsize=(16,16,3))
    #plt.plot(stats["reward_ep"])
    #plt.show()
    if args.recordto:
        #save dictionnary
        stats["episode_starts"][0]=True
        stats["episode_starts"][-1]=False
        np.savez(args.recordto, rewards=stats["rewards"], observations=stats["screens"], actions=np.reshape(stats["actions"],(-1,1)),episode_starts=stats["episode_starts"])
