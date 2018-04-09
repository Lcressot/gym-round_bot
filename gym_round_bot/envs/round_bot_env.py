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

    metadata = {'render.modes': ['human', 'rgb_array']}
                    
    def __init__(self):
        """
        Inits the attributes to None.        
        """        
        self.viewer = None
        self.world = None        
        self.texture = None        
        self.model = None
        self.window = None
        self.observation_space = None
        self.current_observation = None
        self.controller = None        
        self.multiview = None
        # self.action_space -> property
        self.monitor_window = None
        self.crash_stop=None
        self.reward_stop=None
        self._load() # load with loading_vars variables

    @property
    def action_space(self):
        # self.action_space is self.controller.action_space
        return self.controller.action_space

    @property
    def compatible_worlds(self):        
        return {'rb1', # rectangle set, first person view, reward in top left corner
                'rb1_1wall', # rectangle set, first person view, reward in top left corner, middle blocks
                }

    @property
    def compatible_textures(self):        
        return {'minecraft', # minecraft game-like textures
                'colours', # uniform colors, perceptual aliasing !
                'minecraft+', # minecraft game-like textures with other additional antialiasing elements
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
        # check if done
        # stop if crash_stop stop specified and crashed ( in a wall )
        done = False
        done = (done or reward < 0) if self.crash_stop else done
        done = (done or reward > 0) if self.reward_stop else done

        # no info
        info={}
        return self.current_observation, reward, done, {}
        

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
            return self.current_observation
        elif mode == 'human':
            # this slows down rendering with a factor 10 !
            # TODO : show current observation on screen (potentially fusionned image, and not only last render !)
            if not self.window.visible:
                self.window.set_visible(True)
        else: 
            raise Exception('Unknown render mode: '+mode)


    def seed(self, seed=None):
        seed = seeding.np_random(seed)
        return [seed]

    def _load(self):
        """
        Loads a world into environnement with metadata vars

        Parameters used in metadata  for loading :
        - world : the world name to be loaded
        - texture : the texture name to be set on world's walls
        - obssize : the dimensions of the observations (reshaped from window render), if None, no reshape
        - winsize : the dimensions of the observation window (if None, no observation window)
        - controller : the controller of the robot
        - global_pov : a tuple vector of global point of view
        - perspective : Bool for normal perspective. False is orthogonal perspective
        - visible
        - multiview : list of angles for multi-view rendering. The renders will be fusioned into one image
        - focal : the camera focal (<180°)
        - crash_stop = (Bool) Stop when crashing in a wall with negative reward (for speeding dqn learning for instance)
        - reward_stop = (Bool) Stop when reaching reward
        - random_start = (Bool) randomly start from start positions or not
        """
        metadata = RoundBotEnv.metadata
        if not metadata['world'] in self.compatible_worlds:
            raise(Exception('Error: unknown or uncompatible world \'' + metadata['world'] + '\' for environnement round_bot'))
        if not metadata['texture'] in self.compatible_textures:
            raise(Exception('Error: unknown or uncompatible texture \'' + metadata['texture'] + '\' for environnement round_bot'))
        
        ## shared settings
        self.world = metadata['world']
        self.texture = metadata['texture']
        self.random_start = metadata['random_start']
        random_start_rot = ('Theta' in metadata['controller'].controllerType)
        self.model = round_bot_model.Model(world=metadata['world'], random_start_pos=self.random_start, random_start_rot=random_start_rot, texture=metadata['texture'])
        self.obssize = metadata['obssize']
        self.crash_stop = metadata['crash_stop']
        self.reward_stop = metadata['reward_stop']

        # save controller and plug it to model :
        self.controller = metadata['controller']
        self.controller.model = self.model        

        shape = self.obssize
        self.obs_dim = shape[0]*shape[1]*3


        # build main window
        self.window = pygletWindow.MainWindow(  self.model,
                                                global_pov=metadata['global_pov'],
                                                perspective = metadata['perspective'],
                                                interactive=False,
                                                focal=metadata['focal'],
                                                width=metadata['obssize'][0],
                                                height=metadata['obssize'][1],
                                                caption='Round bot in '+self.world+' world',
                                                resizable=False,
                                                visible=metadata['visible']
                                                )

        # build secondary observation window if asked
        if metadata['winsize']:
            self.monitor_window = pygletWindow.SecondaryWindow(self.model,
                                                    global_pov = True,
                                                    perspective = False,
                                                    width=metadata['winsize'][0],
                                                    height=metadata['winsize'][1],
                                                    caption='Observation window '+ self.world,
                                                    resizable=False,
                                                    visible=True,
                                                    )           
            # plug monitor_window to window
            self.window.add_follower(self.monitor_window)

        # observation are RGB images of rendered world (as line arrays)
        self.observation_space = spaces.Box(low=0, high=255, shape=[1, metadata['obssize'][0]*metadata['obssize'][1]*3],dtype=np.uint8)

        self.multiview = metadata['multiview'] # if not None, observations will be fusion of subjective view with given relative xOz angles

    def message(self, message):
        """
        Get message from training and use it if possible
        """
        if self.monitor_window:
            self.monitor_window.message = message



def set_metadata(world='rb1',
                texture='minecraft',
                controller=round_bot_controller.make(name='Theta',dtheta=20,speed=10,int_actions=False,xzrange=2,thetarange=2),
                obssize=[16,16],
                winsize=None,
                global_pov=None,
                perspective=True,
                visible=False,
                multiview=None,
                focal=65.0,
                crash_stop=False,
                reward_stop=False,
                random_start=True,
                ):
    """ static module method for setting loading variables before call to gym.make
    """
    RoundBotEnv.metadata['world'] = world
    RoundBotEnv.metadata['texture'] = texture
    RoundBotEnv.metadata['controller'] = controller
    RoundBotEnv.metadata['obssize'] = obssize
    RoundBotEnv.metadata['winsize'] = winsize
    RoundBotEnv.metadata['global_pov'] = global_pov
    RoundBotEnv.metadata['perspective'] = perspective
    RoundBotEnv.metadata['visible'] = visible
    RoundBotEnv.metadata['multiview'] = multiview
    RoundBotEnv.metadata['focal'] = focal
    RoundBotEnv.metadata['crash_stop'] = crash_stop
    RoundBotEnv.metadata['reward_stop'] = reward_stop
    RoundBotEnv.metadata['random_start'] = random_start
    

set_metadata() # loading with default values
