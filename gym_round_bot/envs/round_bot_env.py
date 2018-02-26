#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018
""" 

import gym

from gym import error, spaces
from gym import utils
from gym.utils import seeding

from gym_round_bot.envs import pygletWindow
from gym_round_bot.envs import round_bot_model
from gym_round_bot.envs import round_bot_controller

import numpy as np


class RoundBotEnv(gym.Env):

    metadata = {'render.modes': ['human', 'rgb_array','rgb_image']}
    
                
    def __init__(self):
        """
        Inits the attributes to None.
        Default world is loaded. Can be changed with call to env.unwrapped.load(newworld,newWinSize)
        """        
        self.viewer = None
        self.world = None        
        self.model = None
        self.window = None
        self.observation_space = None
        self.current_observation = None
        self.controller = None        
        self.multiview = None
        # self.action_space -> property
        self.monitor_window = None
        self.load() #default world loaded

    @property
    def action_space(self):
        # self.action_space is self.controller.action_space
        return self.controller.action_space

    @property
    def compatible_worlds(self):        
        return {'rb1', # rectangle set, first person view, reward in top left corner
                'rb1_blocks', # rectangle set, first person view, reward in top left corner, middle blocks
                }

    @property
    def num_actions(self):
        return self.controller.num_actions
    
    @property
    def actions_mapping(self):
        return self.controller.actions_mapping

    def step(self, action):
        """
        Perform one step
        """
        # perform action
        self.controller.step(action)
        
        # update model and window
        if not self.multiview:
            self.window.step(0.1) # update with 1 second intervall
            # get observation
            self.current_observation = self.window.get_image(reshape=True)
        else:
            self.window.update(0.1) # update with 1 second intervall
            self.current_observation = self.window.multiview_render(self.multiview, as_line=False)

        # get reward :
        reward = self.model.current_reward              

        # this environment has no terminal state and no info
        info = {}
        return self.current_observation, reward, False, info
        

    def reset(self):
        """
        Resets the state of the environment, returning an initial observation.
        Outputs
        -------
        observation : the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        self.model.reset()
        self.current_observation = self.window.get_image(reshape=True)#get image as a numpy line
      
        return self.current_observation
        

    def render(self, mode='human', close=False):

        if mode == 'rgb_array':
            # reshape as line
            return np.reshape(self.current_observation,[1,-1])
        elif mode == 'human':
            # this slows down rendering with a factor 10 !
            # TODO : show current observation on screen (potentially fusionned image, and not only last render !)
            if not self.window.visible:
                self.window.set_visible(True)
        elif mode == 'rgb_image':
            ## reshape line array
            return self.current_observation
        else: 
            raise Exception('Unknown render mode: '+mode)


    def seed(self, seed=None):
        seed = seeding.np_random(seed)
        return [seed]


    def load(self,
            world='rb1',
            controller=round_bot_controller.make(name='Theta',dtheta=20,speed=10,int_actions=False),
            obssize=[16,16],
            winsize=None,
            global_pov=None,
            perspective=True,
            visible=False,
            multiview=None,
            focal=65.0,            
            ):
        """
        Loads a world into environnement

        Parameters :
        - obssize : the dimensions of the observations (reshaped from window render), if None, no reshape
        - winsize : the dimensions of the observation window (if None, no observation window)
        - controller : the controller of the robot
        - global_pov : a tuple vector of global point of view
        - perspective : Bool for normal perspective. False is orthogonal perspective
        - visible
        - multiview : list of angles for multi-view rendering. The renders will be fusioned into one image
        - focal : the camera focal (<180°)
        """
        if not world in self.compatible_worlds:
            raise(Exception('Error: unknown or uncompatible world \'' + world + '\' for environnement round_bot'))
        
        ## shared settings
        self.world = world
        self.model = round_bot_model.Model(world)
        self.obssize = obssize

        # save controller and plug it to model :
        self.controller = controller
        self.controller.model = self.model        

        shape = self.obssize if self.obssize else self.winsize
        self.obs_dim = shape[0]*shape[1]*3

        # build main window
        self.window = pygletWindow.MainWindow(self.model,
                                                global_pov=global_pov,
                                                perspective = perspective,
                                                interactive=False,
                                                focal=focal,
                                                width=obssize[0],
                                                height=obssize[1],
                                                caption='Round bot in '+world+' world',
                                                resizable=False,
                                                visible=visible
                                                )

        # build secondary observation window if asked
        if winsize:
            self.monitor_window = pygletWindow.SecondaryWindow(self.model,
                                                    global_pov = (0,20,0),
                                                    perspective = False,
                                                    width=winsize[0],
                                                    height=winsize[1],
                                                    caption='Observation window '+ world,
                                                    resizable=False,
                                                    visible=True,
                                                    )
            # plug monitor_window to window
            self.window.add_follower(self.monitor_window)

        # observation are RGB images of rendered world (as line arrays)
        self.observation_space = spaces.Box(low=0, high=255, shape=[1, obssize[0]*obssize[1]*3],dtype=np.uint8)

        self.multiview = multiview # if not None, observations will be fusion of subjective view with given relative xOz angles

    def message(self, message):
        """
        Get message from training and use it if possible
        """
        if self.monitor_window:
            self.monitor_window.message = message
