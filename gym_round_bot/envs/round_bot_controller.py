#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018
""" 

from gym_round_bot.envs import round_bot_model
import numpy as np
from gym import spaces
import copy

"""
    This file defines the Controller class for controlling the robot
    In this module, the speed value must be seen as the motor commanded speed,
        and not tha actual speed (which can vary with collisions and friction)
"""
    
##################################################################################################################################
class Controller(object):
    def __init__(self, controllerType, xzrange, thetarange, model=None, noise_ratio=0):
        """
        Abstract class for controllers : controllers are here mappings from actions to model's code execution
        
        Parameters
        ----------
        - controllerType : (string) Describe the controller
        - xzrange : (int, int) x,z speed multiplication factors
        - thetarange : (int) Dtheta multiplication factors
        - model : (round_bot_model) Model controlled by the controller
        - noise_ratio : (float) Ratio to compute additive gaussian noise standard deviation from action's speed
        
        """
        # prevent user from instantiating directly this abstract class
        if type(self) is Controller:
            raise NotImplementedError('Cannot instantiate this abstract class')
        self._controllerType = controllerType
        self._model = model # can be set after initialization
        self._xzrange = xzrange
        self._thetarange = thetarange
        self.action_meaning = '' # string to explain link between actions value and their meaning
        self._action_space = None  # the gym action space corresponding to this controller
        self.noise_ratio = noise_ratio # additive gaussian noise stdv ratio to speed
        self._act = None # function for causing effects of actions
        self._discrete = None # whether controller is discrete, to be setubclassescontrollerType, 

    @property
    def model(self):
        if not model:
            print(Warning('returned model = None'))
        return self._model
    
    @model.setter
    def model(self, model):
        if self._model: # can't assign same controller for several model
            raise Exception('Cannot assign same controller to different models, please create a new controller')
        else: # model must be None here
            self._model = model

    @property
    def num_actions(self):
        raise NotImplementedError()

    @property
    def action_space(self):
        if not self._action_space:
            print(Warning('returned action_space = None'))
        else:
            return self._action_space

    @property
    def speed(self, s):
        self._model.rolling_speed = s

    @property
    def speed(self):
        return self._model.rolling_speed

    @property
    def controllerType(self):
        return copy.copy(self._controllerType)

    @property
    def discrete(self):
        return self._discrete

    def step(self, action):
        """
        Controls the model's robot to perform the action
        Execute functions containded in action functions dictionnary
        """
        # exec action's function
        self._act(*action)



##################################################################################################################################
class DiscreteController(Controller):
    def __init__(self, controllerType, xzrange, thetarange, model=None, int_actions=False, noise_ratio=0):
        """
        parameters:
        ---------
        - int_actions : (Bool) Wether provided actions are of type int
        - *args, **kwargs : see Controller.__init__
        """
        # prevent user from instantiating directly this abstract class
        if type(self) is DiscreteController:
            raise NotImplementedError('Cannot instantiate this abstract class')
        super(DiscreteController, self).__init__(controllerType=controllerType, xzrange=xzrange,
                                                 thetarange=thetarange, model=model, noise_ratio=noise_ratio)
        self._discrete = True
        self._actions = {} # dictionnary to map actions number to their code meaning
        self.int_actions = int_actions
        self._reversed_actions_mapping = None # to be build with self.reverse_actions_mapping afer self._actions initializatio n

    @property
    def num_actions(self):
        return len(self._actions)

    @property
    def action_space_int(self):
        if not self._action_space:
            print(Warning('returned action_space = None'))
        else:
            return spaces.Discrete(self.num_actions-1)

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
        else:
            raise Exception('action_space class name should be either Discrete or MultiDiscrete!')

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

    def step(self, action):
        """
        Controls the model's robot to perform the action
        Execute functions containded in action functions dictionnary
        """
        if self.int_actions:
            # If actions are taken as int, convert them to the correct format
            action = self._reversed_actions_mapping[action]        
        self._act(*action)


##################################################################################################################################
class ContinuousController(Controller):
    def __init__(self, controllerType, xzrange, thetarange, model=None, noise_ratio=0):
        # prevent user from instantiating directly this abstract class
        if type(self) is ContinuousController:
            raise NotImplementedError('Cannot instantiate this abstract class')
        super(ContinuousController, self).__init__(controllerType=controllerType, xzrange=xzrange,
                                                   thetarange=thetarange, model=model, noise_ratio=noise_ratio)
        self._discrete = False

    @property
    def num_actions(self):
        return self._action_space.shape[0]

    def center_reduce_actions(self, actions):
        """
        Center and reduce actions with continuous action space (gym.spaces.Box) parameters
        Return actions in [-1:1] range
        """
        middle = (self._action_space.high + self._action_space.low)/2.0
        maxdist = np.abs(self._action_space.high - self._action_space.low)/2.0
        return (actions - middle)/maxdist


##################################################################################################################################
class Theta_Controller(DiscreteController):
    """ This class controls the robot with 2*thetarange dtheta rotations and speedrange fixed speed forward/bacwkard move
        For Theta controllers, super xzrange parameter is set to speedrange*2
    """
    def __init__(self, model, dtheta, speed, speedrange=1, thetarange=1, int_actions=False, noise_ratio=0):
        super(Theta_Controller,self).__init__('Theta', model=model, xzrange=[speedrange,None], thetarange=thetarange,
                                              int_actions=int_actions, noise_ratio=noise_ratio)
        self.dtheta = dtheta
        self._initial_speed = speed
        self._init()
        self._reversed_actions_mapping = self.reverse_actions_mapping # build reversed action mapping

    def _init(self):
        """ Private initialisation of Theta_Controller
        """
        self.action_meaning = '[s, dth] 2-tuple coding for speed between -initial_speed*2 and +initial_speed*2 and dtheta between -2dt and 2dt'

        self._actions = {(s,d) for s in range(0,2*self._xzrange[0]+1) for d in range(0,2*self._thetarange+1) }
                
        def act(s,d):
            self._model.strafe[0]= 0 if s-self._xzrange[0]==0 else np.sign(s-self._xzrange[0])
            speed = self._initial_speed*(abs(s-self._xzrange[0]))
            self._model.rolling_speed= speed + np.random.normal(0,speed*self.noise_ratio)
            dth = ((d-self._thetarange)*self.dtheta)
            self._model.change_robot_rotation(dth+np.random.normal(0,abs(dth)*self.noise_ratio),0)
        self._act = act

        self._action_space = spaces.MultiDiscrete([2*self._xzrange[0]+1,2*self._thetarange+1])
        # set missing MultiDiscrete parameter n
        self._action_space.n = self.num_actions


##################################################################################################################################
class Theta2_Controller(Theta_Controller):
    """ This class controls the robot like Theta but cannot go backwards
    """
    def __init__(self, model, dtheta, speed, speedrange=1, thetarange=1, int_actions=False, noise_ratio=0):
        super(Theta2_Controller,self).__init__(model=model, dtheta=dtheta, speed=speed, speedrange=speedrange, thetarange=thetarange,
                                               int_actions=int_actions, noise_ratio=noise_ratio)
        self._controllerType = 'Theta2'
        
    def _init(self):
        """ Private initialisation of Theta2_Controller
        """
        self.action_meaning = '[s, dth] 2-tuple coding for speed between 0 and +initial_speed and dtheta between -dt and dt'
        self._actions = { (s,d) for s in range(0,self._xzrange[0]+1) for d in range(0,2*self._thetarange+1) }
        def act(s,d):
            self._model.strafe[0]= 0 if s-self._xzrange[0]==0 else np.sign(s-self._xzrange[0])
            speed = self._initial_speed*abs(s-self._xzrange[0])
            self._model.rolling_speed= speed + np.random.normal(0,speed*self.noise_ratio)
            dth = (d-self._thetarange)*self.dtheta
            self._model.change_robot_rotation(dth+np.random.normal(0,abs(dth)*self.noise_ratio),0)
        self._act = act
                                    
        self._action_space = spaces.MultiDiscrete([1+self._xzrange[0],2*self._thetarange+1])
        # set missing MultiDiscrete parameter n
        self._action_space.n = self.num_actions


##################################################################################################################################
class XZ_Controller(DiscreteController):
    """
    This class controls the robot to move on (oXZ) plan, always looking in the same direction
    """
    def __init__(self, model, speed, xzrange=[1,1], thetarange=2, int_actions=False, noise_ratio=0):
        super(XZ_Controller,self).__init__('XZ',model=model, int_actions=int_actions, xzrange=xzrange,
                                           thetarange=thetarange, noise_ratio=noise_ratio)
        self._initial_speed = speed
        self.action_meaning = '[x, z] 2-tuple coding for x and z between -xzrange and +xzrange'
        self._init()
        self._action_space = spaces.MultiDiscrete([2*xzrange[0]+1,2*xzrange[1]+1])
        # set missing MultiDiscrete parameter n
        self._action_space.n = self.num_actions
        self._reversed_actions_mapping = self.reverse_actions_mapping # build reversed action mapping
        
    def _init(self):
        self._actions = { (x,z) for x in range(0,2*self._xzrange[0]+1) for z in range(0,2*self._xzrange[1]+1)}
        def act(x,z):
            self._model.strafe=[x-self._xzrange[0],z-self._xzrange[1]]
            speed = self._initial_speed*np.sqrt((x-self._xzrange[0])**2+(z-self._xzrange[1])**2)
            self._model.rolling_speed = speed + np.random.normal(0,speed*self.noise_ratio)
        self._act = act              

    @property
    def speed(self, s):
        self._initial_speed = s


##################################################################################################################################
class XZ_Controller_Fixed(XZ_Controller):
    """
    This class controls the robot to move on (oXZ) plan, but always looking in to the same point P
    """
    def __init__(self, model, speed, xzrange=[1,1], thetarange=2, int_actions=False, fixed_point=[0,0], noise_ratio=0):
        super(XZ_Controller_Fixed,self).__init__('XZ fixed', model=model, speed=speed, xzrange=xzrange,
                                                 thetarange=thetarange, int_actions=int_actions, noise_ratio=noise_ratio)
        self._fixed_point = fixed_point
        # set missing MultiDiscrete parameter n
        self._action_space.n = self.num_actions
    
    def _init(self):
        self._actions = { (x,z) for x in range(0,2*self._xzrange[0]+1) for z in range(0,2*self._xzrange[1]+1) }
        def act(x,z):
            self._model.strafe= [x-self._xzrange[0],z-self._xzrange[1]]
            speed = self._initial_speed*np.sqrt((x-self._xzrange[0])**2+(z-self._xzrange[1])**2)
            self._model.rolling_speed = speed + np.random.normal(0,speed*self.noise_ratio)                        
            vec = self._fixed_point-np.array(self._model.robot_position[0:3:2])
            self._model.robot_rotation[0] = 90+np.degrees( np.arctan2( vec[1], vec[0] )  )
        self._act = act


##################################################################################################################################
class XZc_Controller(ContinuousController):
    """
    This class controls the robot to move on (oXZ) plan, always looking in the same direction
    Actions are continuous translations
    """
    def __init__(self, model, speed, xzrange=[1,1], thetarange=2, noise_ratio=0):
        super(XZc_Controller, self).__init__('XZ continuous', model=model, xzrange=xzrange,
                                             thetarange=thetarange, noise_ratio=noise_ratio)
        self.action_meaning = '[a_x, a_z] 2-tuple coding for translations in x and z coordinates between -xzrange and +xzrange'
        self._init()
        self.min_action = np.array([-xzrange[0],-xzrange[1]])
        self.max_action = np.array([xzrange[0],xzrange[1]])
        self._action_space = spaces.Box(low=self.min_action, high=self.max_action, dtype= np.float32)
        self._initial_speed = speed

    def _init(self):
        def act(x, z):
            self._model.strafe=[x,z]
            speed = self._initial_speed*np.sqrt((x)**2+(z)**2)
            self._model.rolling_speed = speed + np.random.normal(0,speed*self.noise_ratio)
        self._act = act

    @property
    def speed(self, s):
        self._initial_speed = s


##################################################################################################################################
class XZca_Controller(ContinuousController):
    """
    This class controls the robot to move on (oXZ) plan, always looking in the same direction
    Actions are continuous acceleration
    """
    def __init__(self, model, xzrange=[1,1], thetarange=2, noise_ratio=0):
        super(XZca_Controller, self).__init__('XZ continous acceleration', model=model, xzrange=xzrange,
                                              thetarange=thetarange, noise_ratio=noise_ratio)
        self.action_meaning = '[a_x, a_z] 2-tuple coding for accelerations in x and z coordinates between -xzrange and +xzrange'
        self._init()
        self.min_action = np.array([-xzrange[0],-xzrange[1]])
        self.max_action = np.array([xzrange[0],xzrange[1]])
        self._action_space = spaces.Box(low=self.min_action, high=self.max_action, dtype= np.float32)

    def _init(self):
        def act(x, z):
            self._model.acceleration = [x, z]
        self._act = act

    @property
    def speed(self, s):
        raise Exception('cannot modify speed for this controller, only accelerations')


def make(name, speed=5, dtheta=7.0, xzrange=[1,1], speedrange=1, thetarange=1, int_actions=False, model=None, fixed_point=[0,0],noise_ratio=0.0):
    """
    Functions for making controller objects
    """
    compatible_controllers = {'Theta','Theta2','XZ','XZF','XZc','XZca'}
    noise_ratio = float(noise_ratio)

    if name=='Theta':
        return Theta_Controller(model=model, dtheta=dtheta,speed=speed, int_actions=int_actions, speedrange=speedrange, thetarange=thetarange, noise_ratio=noise_ratio)
    elif name=='Theta2':
        return Theta2_Controller(model=model, dtheta=dtheta, speed=speed, int_actions=int_actions, speedrange=speedrange, thetarange=thetarange, noise_ratio=noise_ratio)
    elif name=='XZ':        
        return XZ_Controller(model=model, speed=speed, int_actions=int_actions, xzrange=xzrange, thetarange=thetarange, noise_ratio=noise_ratio)
    elif name=='XZca':
        return XZca_Controller(model=model, xzrange=xzrange, thetarange=thetarange, noise_ratio=noise_ratio)
    elif name=='XZc':
        return XZc_Controller(model=model, speed=speed, xzrange=xzrange, thetarange=thetarange, noise_ratio=noise_ratio)
    elif name=='XZF':
        return XZ_Controller_Fixed(model=model, speed=speed, int_actions=int_actions, fixed_point=fixed_point, xzrange=xzrange, thetarange=thetarange, noise_ratio=noise_ratio)
    else :
        raise ValueError('unknown or uncompatible controller name \'' + name + '\'. Compatible controllers are : '+str(compatible_controllers))
