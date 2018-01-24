import gym

from gym import error, spaces
from gym import utils
from gym.utils import seeding

try:
    import round_bot_model
    import pygletWindow
except ImportError as e:
    # TODO : set dependencies for round_bot (pyglet)
    raise error.DependencyNotInstalled("{}. (HINT: you can install round_bot dependencies by running 'pip install gym[round_bot]'.)".format(e))

import logging
logger = logging.getLogger(__name__)

COMPATIBLE_WORLDS={"rb1", # rectangle set, first person view, reward in top left corner
}

class RoundBotEnv(gym.Env):

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self):

        self.viewer = None
        self.world = None        
        self.model = None
        self.winSize= None
        self.window = None
        self.observation_space = None
        self.action_space = None        
        self.current_observation = None
        self._loaded = False
        self.load_env()
                

    def _step(self, a):
        """
        Perform one step
        """
        reward = 0.0
        action = self.action_meaning[a]

        if self.world == "rb1":
            # perform action
            if action == "MOVEFORWARD":
                self.model.strafe[0] = 1
            elif action == "STOP":
                self.model.strafe[0] = 0
            elif action == "ROTATERIGHT":
                self.model.change_robot_rotation(10,0)
            else: # action = "ROTATELEFT"
                self.model.change_robot_rotation(-10,0)

            # update
            self.window.step(0.1) # update with 1 second intervall
            
            # reward -1 if agent bumps into a wall
            if self.model.collided:
                reward = reward - 1.0
            # reward 1 if agent is in top right corner of the rectangle world with radius 0.3 * width
            x,y,z = self.model.robot_position
            w = self.model.world_info["width"]
            d = self.model.world_info["depth"]
            # check distance to top right corner
            if (x-w/2.0)**2 + (z-d/2.0)**2 < (0.3*min(w,d)/2.0)**2:
                reward = reward + 1.0
            # reward 0 else                 

        self.current_observation = self.window.get_image()
        info = {}

        # this environment has no terminal state
        return self.current_observation, reward, False, info
        

    def _reset(self):
        """
        Resets the state of the environment, returning an initial observation.
        Outputs
        -------
        observation : the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        self.model.reset()
        return self.window.get_image()
        

    # @property
    # def action_space(self):
    #   """
    #   Returns a Space object
    #   """
    #   return self.action_space

    # @property
    # def observation_space(self):
    #   """
    #   Returns a Space object
    #   """
    #   return self.observation_space

    def _render(self, mode='human', close=False):
        
        if mode == 'rgb_array':
            return self.current_observation
        elif mode == 'human':
            self.window.set_visible(True)

    def load_env(self, world='rb1', winsize=[800,600]):
        """
        Loads a world into environnement
        """
        if not world in COMPATIBLE_WORLDS:
            raise(Exception('Error: unknown or uncompatible world \"' + world + '\" for environnement round_bot'))

        # unic world settings
        if world == 'rb1':

            self.action_meaning = {
            0 : "MOVEFORWARD",
            1 : "STOP",
            2 : "ROTATERIGHT",
            3 : "ROTATELEFT",    
            }
        else:
            raise(Exception('Error: world '+ world +' should figure in code enumeration if elif..'))
            
        # shared settings
        self.world = world
        
        # try:
        #     self.model = round_bot_model.Model(world)
        # except Exception, e:
        #     print("Error : Could not create model for world : "+world)
        self.model = round_bot_model.Model(world)
        self.winSize= list(winsize)

        #try:
        self.window = pygletWindow.PygletWindow(self.model, width=winsize[0], height=winsize[1], caption='Round bot in '+world+' world', resizable=False, visible=False)
        # except Exception, e:
        #   print("Error : Could not create window for world : "+world)
        
            # observation are RGB images of rendered world      
        self.observation_space = spaces.Box(low=0, high=255, shape=[winsize[0], winsize[1], 3])
        self.action_space = spaces.Discrete(len(self.action_meaning))
        # first observation
        self.current_observation = self.window.get_image()
        self._loaded = True

    def get_action_meanings(self):
        return [self.action_meaning[i] for i in self.action_space]


    
