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
    def __init__(self, controllerType, xzrange, thetarange, model=None, int_actions=False):
        """
            Abstract class for controllers : i.e actions to code exectution mappings
            int_actions : bool for taking int actions
        """
        self._model = model # can be set after initialization
        self._xzrange = xzrange
        self._thetarange = thetarange
        self.controllerType = controllerType # type of actions : ex int for integers, tuple2 for (x,y) tuples, float...
        self.action_meaning = {} # dictionnary to map actions number to their string meaning
        self._actions = {} # dictionnary to map actions number to their code meaning
        self.int_actions = int_actions
        self._action_space = None  # the gym action space corresponding to this controller
        self._reversed_actions_mapping = None # to be build with self.reverse_actions_mapping afer self._actions initializatio n

    @property
    def model(self):
        if not model:
            print(Warning('returned model = None'))
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
        # Easiest way of doing it :
        # keys = self._actions.keys()
        # return dict( zip(keys, range(len(keys))) )

        # We choose the more way also implemented in our action_wrapper
        action_space = self._action_space
        name=type(action_space).__name__
        if name == 'Discrete':
            return {i:i for i in range(action_space.n)}
        elif name =='MultiDiscrete':
            r=[[]]
            for x in action_space.nvec:
                t = []
                for y in list(range(x)):
                    for i in r:
                        t.append(i+[y])
                r = t
            return {tuple(r[i]): i for i in range(len(r))}

    @property
    def reverse_actions_mapping(self):
        """
        Returns a mapping from integers indices to action. Ex: {0:(0,0), 1:(0,1), 2:(1,0)}
        """
        # Easiest way of doing it :
        # keys = self._actions.keys()
        # return dict( zip( range(len(keys)), keys) )

        # We choose the more way also implemented in our action_wrapper
        actions_mapping = self.actions_mapping
        return {actions_mapping[k]:k for k in actions_mapping.keys()}


    @property
    def action_space(self):
        if not self._action_space:
            print(Warning('returned action_space = None'))
        elif self.int_actions: # return a Discrete space if int_actions is True
            return spaces.Discrete(self.num_actions-1)
        else:
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
    """ This class controls the robot with 2*thetarange dtheta rotations and xzrange fixed speed forward/bacwkard move
    """
    def __init__(self, model, dtheta, speed, int_actions=int, xzrange=2, thetarange=2):
        super(Theta_Controller,self).__init__('Theta tuple2',model=model, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange)
        self.dtheta = dtheta
        self._initial_speed = speed
        self._init()
        self._reversed_actions_mapping = self.reverse_actions_mapping # build reversed action mapping

    def _init(self):
        """ Private initialisation of Theta_Controller
        """
        self.action_meaning = '[s, dth] 2-tuple coding for speed between -initial_speed*2 and +initial_speed*2 and dtheta between -2dt and 2dt'
        self._actions = { (s,d) : 'self._model.strafe[0]='+str(0 if s-self._xzrange==0 else np.sign(s-self._xzrange))
                                    +'; self._model.walking_speed=self._initial_speed*'+str(abs(s-self._xzrange))+';'
                                    +'self._model.change_robot_rotation('+str((d-self._thetarange)*self.dtheta)+',0);'
                                    for s in range(0,2*self._xzrange+1) for d in range(0,2*self._thetarange+1) }
        self._action_space = spaces.MultiDiscrete([2*self._xzrange+1,2*self._thetarange+1])

    @property
    def speed(self, s):
        self._model.walking_speed = s

    @property
    def speed(self):
        return self._model.walking_speed


class Theta2_Controller(Theta_Controller):
    """ This class controls the robot like Theta but cannot go backwards
    """
    def __init__(self, model, dtheta, xzrange=1, thetarange=1, speed=10.0, int_actions=False):
        super(Theta2_Controller,self).__init__(model, dtheta=dtheta, speed=speed, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange)        
        
    def _init(self):
        """ Private initialisation of Theta2_Controller
        """
        self.action_meaning = '[s, dth] 2-tuple coding for speed between 0 and +initial_speed and dtheta between -dt and dt'
        self._actions = { (s,d) : 'self._model.strafe[0]='+str(np.sign(-s))
                                    +';self._model.change_robot_rotation('+str((d-self._thetarange)*self.dtheta)+',0);'
                                    for s in range(0,self._xzrange+1) for d in range(0,2*self._thetarange+1) }
        self._action_space = spaces.MultiDiscrete([1+self._xzrange,2*self._thetarange+1])


class XZ_Controller(Controller):
    """
    This class controls the robot to move on (oXZ) plan, always looking in the same direction
    """
    def __init__(self, model, speed, xzrange=2, thetarange=2, int_actions=False):
        super(XZ_Controller,self).__init__('XZ tuple2', model=model, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange)
        self._initial_speed = speed
        self.action_meaning = '[x, z] 2-tuple coding for x and z between -xzrange and +xzrange'
        self._init()
        self._action_space = spaces.MultiDiscrete([2*xzrange+1,2*xzrange+1])
        self._reversed_actions_mapping = self.reverse_actions_mapping # build reversed action mapping
        
    def _init(self):
        self._actions = { (x,z) : 'self._model.strafe='
                        +str([x-self._xzrange,z-self._xzrange])+'; self._model.walking_speed=self._initial_speed*'
                        +str(np.sqrt((x-self._xzrange)**2+(z-self._xzrange)**2))
                        for x in range(0,2*self._xzrange+1) for z in range(0,2*self._xzrange+1)
                        }

    @property
    def speed(self, s):
        self._initial_speed = s

    @property
    def speed(self):
        return self._model.walking_speed


class XZ_Controller_Fixed(XZ_Controller):
    """
    This class controls the robot to move on (oXZ) plan, but always looking in to the same point P
    """
    def __init__(self, model, speed, xzrange=2, thetarange=2, int_actions=False, fixed_point=[0,0]):
        super(XZ_Controller_Fixed,self).__init__(model=model, speed=speed, xzrange=xzrange, thetarange=thetarange, int_actions=int_actions)
        self._fixed_point = fixed_point
    
    def _init(self):
        self._actions = { (x,z) : 'self._model.strafe='
                        +str([x-self._xzrange,z-self._xzrange])+'; self._model.walking_speed=self._initial_speed*'
                        +str(np.sqrt((x-self._xzrange)**2+(z-self._xzrange)**2))
                        +'; vec=self._fixed_point-np.array(self._model.robot_position[0:3:2]);'
                        +'self._model.robot_rotation[0] = 90+np.degrees( np.arctan2( vec[1], vec[0] )  )'
                        for x in range(0,2*self._xzrange+1) for z in range(0,2*self._xzrange+1)
                        }

def make(name, speed=5, dtheta=7.0, xzrange=1, thetarange=1, int_actions=False, model=None, fixed_point=[0,0]):
    """
    Functions for making controller objects
    """
    compatible_controllers = {'Theta, Theta2, XZ, XZF'}

    if name=='Theta':
        return Theta_Controller(model=model, dtheta=dtheta,speed=speed, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange)

    elif name=='Theta2':
        return Theta2_Controller(model=model, dtheta=dtheta,speed=speed, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange)

    elif name=='XZ':        
        return XZ_Controller(model=model, speed=speed, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange)

    elif name=='XZF':
        return XZ_Controller_Fixed(model=model, speed=speed, int_actions=int_actions, fixed_point=fixed_point, xzrange=xzrange, thetarange=thetarange)

    else :
        raise Exception('unknown or uncompatible controller name \'' + name + '\'. Compatible controllers are : '+str(compatible_controllers))


