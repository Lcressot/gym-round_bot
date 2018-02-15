#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018
""" 

from gym_round_bot.envs import round_bot_model
import numpy as np

"""
    This file defines the Controller class for controlling the robot
"""
    
class Controller(object):
    def __init__(self, model, controllerType):
        self._model = model
        self.controllerType = controllerType # type of actions : ex int for integers, tuple2 for (x,y) tuples, float...
        self.action_meaning = {} # dictionnary to map actions number to their string meaning
        self._actions = {} # dictionnary to map actions number to their code meaning

    @property
    def num_actions(self): # num_actions is a constant private parameter
        raise Exception("Not implemented error : num_actions not implemented for Controller abstract class")

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

    def step(self, action):
        """
        Controls the model's robot to perform the action
        Execute code containded in actions dictionnary
        """
        exec(self._actions[action])


class Theta_Controller(Controller):
    """
    This class controls the robot with fixed dtheta rotations and fixed speed forward move
    """
    def __init__(self, model, dtheta, speed):
        super(Theta_Controller,self).__init__(model,'int')
        self.dtheta = dtheta
        self._initial_speed = speed
        self.action_meaning = '[s, dth] 2-tuple coding for speed between -initial_speed*2 and +initial_speed*2 and dtheta between -2dt and 2dt'
        self._actions = { (s,d) : 'self._model.strafe[0]='+str(np.sign(s))
                                    +'; self._model.walking_speed=self._initial_speed*'+str(s-2)+';'
                                    +'self._model.change_robot_rotation('+str((d-2)*self.dtheta)+',0);'
                                    for s in range(0,2*2+1) for d in range(0,5) }

    @property
    def speed(self, s):
        self._model.walking_speed = s

    @property
    def speed(self):
        return self._model.walking_speed


class XZ_Controller(Controller):
    """
    This class controls the robot to move on (oXZ) plan, always looking in the same direction
    """
    def __init__(self, model, speed, xzrange):
        super(XZ_Controller,self).__init__(model,'tuple2')
        self._initial_speed = speed
        self._xzrange = xzrange # how many maximum xz units you can move at once
        self.action_meaning = '[x, z] 2-tuple coding for x and z between -xzrange and +xzrange'
        self._actions = { (x,z) : 'self._model.strafe='+str([x-xzrange,z-xzrange])+'; self._model.walking_speed=self._initial_speed*'+str(np.sqrt((x-xzrange)**2+(z-xzrange)**2)) for x in range(0,2*xzrange+1) for z in range(0,2*xzrange+1) }

    @property
    def speed(self, s):
        self._initial_speed = s

    @property
    def speed(self):
        return self._initial_speed
