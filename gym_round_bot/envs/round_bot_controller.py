#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018
""" 

from gym_round_bot.envs import round_bot_model
import numpy as np
from gym import spaces

"""
    This file defines the Controller class for controlling the robot
"""
    
class Controller(object):
    def __init__(self, controllerType, model=None, int_actions=False):
        """
            Abstract class for controllers : i.e actions to code exectution mappings
            int_actions : bool for taking int actions
        """
        self._model = model # can be set after initialization
        self.controllerType = controllerType # type of actions : ex int for integers, tuple2 for (x,y) tuples, float...
        self.action_meaning = {} # dictionnary to map actions number to their string meaning
        self._actions = {} # dictionnary to map actions number to their code meaning
        self.int_actions = int_actions
        self._action_space = None  # the gym action space corresponding to this controller
        self._reversed_actions_mapping = None # to be build with self.reverse_actions_mapping afer self._actions initializatio n


    @property
    def model(self):
        return self._model
    
    @model.setter
    def model(self, model):
        self._model = model

    @property
    def num_actions(self):
        return len(self._actions)

    @property
    def actions_mapping(self):
        """
        Returns a mapping from actions to integer indices. Ex: {(0,0):0, (0,1):1, (1,0):2}
        """
        keys = self._actions.keys()
        return dict( zip(keys, range(len(keys))) )        

    @property
    def reverse_actions_mapping(self):
        """
        Returns a mapping from integers indices to action. Ex: {0:(0,0), 1:(0,1), 2:(1,0)}
        """
        keys = self._actions.keys()
        return dict( zip( range(len(keys)), keys) )

    @property
    def action_space(self):
        return self._action_space

    def step(self, action):
        """
        Controls the model's robot to perform the action
        Execute code containded in actions dictionnary
        """
        if self.int_actions:
            # If actions are taken as int, convert them to the correct format
            action = self._reversed_actions_mapping[action]
            
        exec(self._actions[action])



class Theta_Controller(Controller):
    """ This class controls the robot with 2 fixed dtheta rotations and 2 fixed speed forward/bacwkard move
    """
    def __init__(self, model, dtheta, speed, int_actions):
        super(Theta_Controller,self).__init__('Theta tuple2',model, int_actions)
        self.dtheta = dtheta
        self._initial_speed = speed
        self._init()
        self._reversed_actions_mapping = self.reverse_actions_mapping # build reversed action mapping

    def _init(self):
        """ Private initialisation of Theta_Controller
        """
        self.action_meaning = '[s, dth] 2-tuple coding for speed between -initial_speed*2 and +initial_speed*2 and dtheta between -2dt and 2dt'
        self._actions = { (s,d) : 'self._model.strafe[0]='+str(0 if s-2==0 else np.sign(s-2))
                                    +'; self._model.walking_speed=self._initial_speed*'+str(abs(s-2))+';'
                                    +'self._model.change_robot_rotation('+str((d-2)*self.dtheta)+',0);'
                                    for s in range(0,2*2+1) for d in range(0,5) }
        self._action_space = spaces.MultiDiscrete([5,5])

    @property
    def speed(self, s):
        self._model.walking_speed = s

    @property
    def speed(self):
        return self._model.walking_speed


class Theta2_Controller(Theta_Controller):
    """ This class controls the robot with fixed dtheta rotations and fixed speed forward (no backward) move
    """
    def __init__(self, model, dtheta, speed, int_actions):
        super(Theta2_Controller,self).__init__(model, dtheta, speed, int_actions)        
        
    def _init(self):
        """ Private initialisation of Theta2_Controller
        """
        self.action_meaning = '[s, dth] 2-tuple coding for speed between 0 and +initial_speed and dtheta between -dt and dt'
        self._actions = { (s,d) : 'self._model.strafe[0]='+str(-s)
                                    +';self._model.change_robot_rotation('+str((d-1)*self.dtheta)+',0);'
                                    for s in range(0,2) for d in range(0,2+1) }
        self._action_space = spaces.MultiDiscrete([2,3])


class XZ_Controller(Controller):
    """
    This class controls the robot to move on (oXZ) plan, always looking in the same direction
    """
    def __init__(self, model, speed, xzrange=2, int_actions=False):
        super(XZ_Controller,self).__init__('XZ tuple2', model, int_actions)
        self._initial_speed = speed
        self._xzrange = xzrange # how many maximum xz units you can move at once
        self.action_meaning = '[x, z] 2-tuple coding for x and z between -xzrange and +xzrange'
        self._actions = { (x,z) : 'self._model.strafe='+str([x-xzrange,z-xzrange])+'; self._model.walking_speed=self._initial_speed*'+str(np.sqrt((x-xzrange)**2+(z-xzrange)**2)) for x in range(0,2*xzrange+1) for z in range(0,2*xzrange+1) }
        self._action_space = spaces.MultiDiscrete([2*xzrange+1,2*xzrange+1])
        self._reversed_actions_mapping = self.reverse_actions_mapping # build reversed action mapping

    @property
    def speed(self, s):
        self._initial_speed = s

    @property
    def speed(self):
        return self._model.walking_speed



def make(name, speed, dtheta=0.0, xzrange=2, int_actions=False, model=None):
    """
    Functions for making controller objects
    """
    compatible_controller = {'Theta, XZ'}

    if name=='Theta':
        return Theta_Controller(model=model, dtheta=dtheta,speed=speed, int_actions=int_actions)

    elif name=='Theta2':
        return Theta2_Controller(model=model, dtheta=dtheta,speed=speed, int_actions=int_actions)

    elif name=='XZ':        
        return XZ_Controller(model=model, speed=speed, int_actions=int_actions, xzrange=xzrange)

    else :
        raise Exception('unknown or uncompatible controller name \'' + name + '\'. Compatible controllers are : '+str(compatible_controller))


