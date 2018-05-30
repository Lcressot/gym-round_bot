#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic & Merckling Astrid
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
import copy


class RoundBotEnv(gym.Env):

    metadata = {'render.modes': ['human', 'rgb_array']}
                    
    def __init__(self):
        """
        Inits the attributes to None.        
        """        
        self._world = None        
        self._texture = None        
        self._model = None
        self._window = None
        self._observation_space = None
        self._current_observation = None
        self._controller = None        
        self._multiview = None
        # self.action_space -> property
        self._monitor_window = None
        self._crash_stop = None
        self._reward_stop = None
        self._reward_count_stop = None
        self._reward_count = 0.0
        self._normalize_observations = None
        self._normalize_rewards = None
        self._observation_transformation = None
        self._position_observations = None
        self._get_observation = None # function to get current observation (which transforms and reshapes it if asked)
        self._sandboxes = None
        self._trigger_buttonutton = None
        self._distractors = None
        self._load() # load with loading_vars variables

    def __del__(self):
        """
        Cleans the env object before env deletion        
        trigger_button = self._trigger_button,
        """
        if self._monitor_window:
            self.delete_monitor_window()
        if self._window:
            try:
                self._window.close()
            except ImportError: # happens sometimes
                pass

    @property
    def action_space(self):
        # self.action_space is self._controller.action_space
        return self._controller.action_space

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
        return self._controller.num_actions
    
    @property
    def actions_mapping(self):
        return self._controller.actions_mapping

    @property
    def ground_truth(self):
        """ Returns currents ground truth, i.e robot position and rotation. Warning : return copy and not the object
        """
        return copy.copy(self._model.robot_position), copy.copy(self._model.robot_rotation)

    @property
    def controller(self):
        return self._controller
    

    def step(self, action):
        """
        Perform one step
        """
        # perform action
        self._controller.step(action)
        
        # update model and window
        if not self._multiview:
            self._window.step(0.1) # update with 0.1 second intervall               
            # get observation
            self._current_observation = self._get_observation()
        else:
            self._window.update(0.1) # update with 0.1 second intervall
            # get observation
            self._current_observation = self._window.multiview_render(self._multiview)
       

        # get reward :
        reward = self._model.current_reward
        # update self._reward_count
        self._reward_count += reward
        # check if done
        done = ((self._crash_stop and reward < 0) or
               (self._reward_stop and reward > 0) or
               (self._reward_count_stop and self._reward_count <= self._reward_count_stop))        
        
        # normalize rewards if asked
        if self._normalize_rewards:
            reward = reward/self._model.max_reward # normalize values in [-1,1] float range
        # no info
        info={}
        return self._current_observation, reward, done, {}
        

    def reset(self):
        """
        Resets the state of the environment, returning an initial observation.
        Outputs
        -------
        observation : the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        self._model.reset()
        self._reward_count=0.0
        self.unwrapped._model.speed_continuous = np.array([0, 0], dtype=float)
        
        # get observation
        self._current_observation = self._get_observation()
      
        return self._current_observation
        

    def render(self, mode='human', close=False):

        if mode == 'rgb_array':
            # reshape as line
            return self._current_observation
        elif mode == 'human':
            # this slows down rendering with a factor 10 !
            # TODO : show current observation on screen (potentially fusionned image, and not only last render !)
            if not self._window.visible:
                self._window.set_visible(True)
        else: 
            raise ValueError('Unknown render mode: '+mode)


    def seed(self, seed=None):
        seed = seeding.np_random(seed)
        return [seed]

    def _load(self):
        """
        Loads a world into environnement with metadata vars

        Parameters used in metadata for loading :
            -> see in load_metada method
        """
        metadata = RoundBotEnv.metadata
        if not metadata['world'] in self.compatible_worlds:
            raise(Exception('Error: unknown or uncompatible world \'' + metadata['world'] + '\' for environnement round_bot'))
        if not metadata['texture'] in self.compatible_textures:
            raise(Exception('Error: unknown or uncompatible texture \'' + metadata['texture'] + '\' for environnement round_bot'))
        
        ## shared settings
        self._world = metadata['world']
        self._texture = metadata['texture']
        self.random_start = metadata['random_start']
        random_start_rot = ('Theta' in metadata['controller'].controllerType)
        self._distractors = RoundBotEnv.metadata['distractors']
        self._sandboxes = RoundBotEnv.metadata['sandboxes']
        self._trigger_button = RoundBotEnv.metadata['trigger_button']
        self._model = round_bot_model.Model(world=metadata['world'],
                                            random_start_pos=self.random_start,
                                            random_start_rot=random_start_rot,
                                            texture=metadata['texture'],
                                            distractors=self._distractors,
                                            sandboxes=self._sandboxes,
                                            trigger_button = self._trigger_button,
                                            )
        self.obssize = metadata['obssize']
        self._crash_stop = metadata['crash_stop']
        self._reward_count_stop = metadata['reward_count_stop']
        self._reward_stop = metadata['reward_stop']

        # save controller and plug it to model :
        self._controller = metadata['controller']
        self._controller.model = self._model
        self._normalize_rewards = metadata['normalize_rewards']     
        self._normalize_observations = metadata['normalize_observations']     
        self._observation_transformation = metadata['observation_transformation']     
        self._position_observations = metadata['position_observations']

        shape = self.obssize
        self.obs_dim = shape[0]*shape[1]*3


        # build main window
        self._window = pygletWindow.MainWindow(  self._model,
                                                global_pov=metadata['global_pov'],
                                                perspective = metadata['perspective'],
                                                interactive=False,
                                                focal=metadata['focal'],
                                                width=metadata['obssize'][0],
                                                height=metadata['obssize'][1],
                                                caption='Round bot in '+self._world+' world',
                                                resizable=False,
                                                visible=metadata['visible']
                                                )

        # build secondary observation window if asked
        if metadata['winsize']:
            self._monitor_window = pygletWindow.SecondaryWindow(self._model,
                                                    global_pov = True,
                                                    perspective = False,
                                                    width=metadata['winsize'][0],
                                                    height=metadata['winsize'][1],
                                                    caption='Observation window '+ self._world,
                                                    resizable=False,
                                                    visible=True,
                                                    )           
            # plug monitor_window to window
            self._window.add_follower(self._monitor_window)

        # observation are RGB images of rendered world (as line arrays)
        self._observation_space = spaces.Box(low=0, high=255, shape=[1, metadata['obssize'][0]*metadata['obssize'][1]*3],dtype=np.uint8)

        self._multiview = metadata['multiview'] # if not None, observations will be fusion of subjective view with given relative xOz angles

        ## build self._get_observation function, which gets current observation (which transforms and reshapes it if asked)
        # observation getter
        self._get_observation = self._build_observation_getter()

    def _build_observation_getter(self):
        """
        Builds the function for getting observation, given following initiliazation parameters : 
            self._position_observations , self._normalize_observations, and self._position_observations
        This way of doing allows clarity and fast processing of step function by avoiding calls to if statements and lambda functions
        """
        if not self._position_observations :            
            to_eval = 'self._window.get_image()'
        else: # observations are arrays of positions of mobable blocks           
            to_eval = 'self._model.position_observation()'
        
        if self._normalize_observations:
            if not self._position_observations:
                to_eval += '*2.0/255.0 - 1.0' # normalize from int [0:255] range to float [-1:1] range
            else:
                w=self._model.world_info['width']
                to_eval += '/' + str([w,w,w,360.0,360.0,360.0]) # normalize position with w and rotation with 360

        if self._observation_transformation:
            to_eval = 'self._observation_transformation(' + to_eval + ')'
        to_eval = 'lambda : ' + to_eval
        return eval(to_eval,{'self':self}) # pass self as variable

    def message(self, message):
        """
        Get message from training and use it if possible
        """
        if self._monitor_window:
            self._monitor_window.message = message

    def add_monitor_window(self, height, width):
        """
        adds a monitor window if there are none yet
        """
        if not (height > 0 and width > 0):
            raise ValueError('unvalid dimensions for monitor window')
        if not self._monitor_window:
            self._monitor_window = pygletWindow.SecondaryWindow(
                                        self._model,
                                        global_pov = True,
                                        perspective = False,
                                        width=height,
                                        height=width,
                                        caption='Observation window '+ self._world,
                                        resizable=False,
                                        visible=True,
                                        )           
            # plug monitor_window to window
            self._window.add_follower(self._monitor_window)
        else:
            raise Warning('a monitor window has already been added !')

    def delete_monitor_window(self):
        """
        deletes the monitor window
        """
        if not self._monitor_window:
            raise Warning('no monitor window to delete')
        else:
            self._window.remove_follower(self._monitor_window)
            self._monitor_window.close()
            del self._monitor_window
            self._monitor_window = None


def set_metadata(world='rb1',
                texture='minecraft',
                controller=round_bot_controller.make(name='Theta',dtheta=20,speed=10,int_actions=False,xzrange=[2,2],thetarange=2),
                obssize=[16,16],
                winsize=None,
                global_pov=None,
                perspective=True,
                visible=False,
                multiview=None,
                focal=65.0,
                crash_stop=False,
                reward_stop=False,
                reward_count_stop = False,
                random_start=True,
                normalize_observations=False,
                normalize_rewards=False,
                observation_transformation = None,
                position_observations = False,
                distractors = False,
                sandboxes=False,
                trigger_button=False,
                ):
    """ static module method for setting loading variables before call to gym.make

        parameters :
        -----------
        - world : (str) name of the world to load
        - texture : (str) name of texture to set to world brick blocks
        - controller: (round_bot_Controller) controller object to use for mapping from actions to robot control
        - obssize / winsize : (tuple(int)) observation's / monitor windows's size tuple
        - global_pov : (Tuple(float,float,float) or Bool or None) global point of view tuple.
            Set True for automatic computing and None if none
        - perspective : (Bool) If True, perspective is projective, else it is orthogonal
        - visible : (Bool) If True the main window will be shown (slows down rendering)
        - multiview : List(float) List of angles for multi-view rendering. The renders will be fusioned into one image.
        - focal : float (<180°) The camera focal
        - crash_stop : (Bool) Wether to stop when crashing in a wall with negative reward (for speeding dqn learning for instance)            
        - reward_count_stop: (int or False) If not False, stop when the sum of rewards (before normalization) reaches this value.
        - reward_stop : (Bool) Wether to stop when reaching positive reward            
        - random_start : (Bool) Randomly start from start positions or not
        - normalize_observations : (Bool) Rescale observations from (int)[0:255] range to (float)[-1:1] with X -> X * 2.0/255 -1.0
        - normalize_rewards : (Bool) Rescale rewards to (float)[-1:1] range by dividing rewards by world's highest abs reward value
        - observation_transformation : (function) apply observation_transformation function to observations after normalization
        - position_observations: (Bool) observations are not images (np.array([w,h,c])) but [X, Y, Z, rx, ry, rz] np.arrays of 
            every moving blocks in the scene
        - distractors (Bool) : whether to add visual distractors on walls or not
        - sandboxes (Bool): whether to add sandboxes on the ground or not (slowing down the robot when crossed)
        - trigger_button (Bool): whether to add a trigger button 
    """
    RoundBotEnv.metadata['world'] = world
    RoundBotEnv.metadata['texture'] = texture
    RoundBotEnv.metadata['controller'] = controller
    RoundBotEnv.metadata['obssize'] = obssize
    RoundBotEnv.metadata['winsize'] = winsize
    RoundBotEnv.metadata['global_pov'] = global_pov
    RoundBotEnv.metadata['perspective'] = perspective # 
    RoundBotEnv.metadata['visible'] = visible
    RoundBotEnv.metadata['multiview'] = multiview
    RoundBotEnv.metadata['focal'] = focal
    RoundBotEnv.metadata['crash_stop'] = crash_stop
    RoundBotEnv.metadata['reward_count_stop'] = reward_count_stop
    RoundBotEnv.metadata['reward_stop'] = reward_stop
    RoundBotEnv.metadata['random_start'] = random_start
    RoundBotEnv.metadata['normalize_observations'] = normalize_observations
    RoundBotEnv.metadata['normalize_rewards'] = normalize_rewards
    RoundBotEnv.metadata['observation_transformation'] = observation_transformation
    RoundBotEnv.metadata['position_observations'] = position_observations
    RoundBotEnv.metadata['distractors'] = distractors
    RoundBotEnv.metadata['sandboxes'] = sandboxes
    RoundBotEnv.metadata['trigger_button'] = trigger_button

    

set_metadata() # loading with default values
