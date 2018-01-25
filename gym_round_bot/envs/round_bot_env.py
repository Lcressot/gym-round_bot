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

COMPATIBLE_WORLDS={ "null_world", # void world used for fast initialisation
                    "rb1", # rectangle set, first person view, reward in top left corner
}

class RoundBotEnv(gym.Env):

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self):
        """
        Inits the attributes to None.
        Default world is loaded. Can be changed with call to env.unwrapped.load(newworld,newWinSize)
        """

        self.viewer = None
        self.world = None        
        self.model = None
        self.winSize= None
        self.window = None
        self.observation_space = None
        self.action_space = None        
        self.current_observation = None
        self.action_meaning = None        
        self.load() #default world loaded
                

    def _step(self, action):
        """
        Perform one step
        """
        reward = 0.0

        if self.world == "rb1":
            # perform action
            if action == 0: #MOVE FORFORWARD
                self.model.strafe[0] = 1
            elif action == 1: # STOP
                self.model.strafe[0] = 0
            elif action == 2: # "ROTATERIGHT"
                self.model.change_robot_rotation(20,0)
            else: # action = 3 for "ROTATELEFT"
                self.model.change_robot_rotation(-20,0)

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
        

    def _render(self, mode='human', close=False):

        if mode == 'rgb_array':
            return self.current_observation
        elif mode == 'human':
            # this slows down rendering with a factor 10 !
            if not self.window.visible:
                self.window.set_visible(True)

    def load(self, world='rb1', winsize=[80,60]):
        """
        Loads a world into environnement
        """
        if not world in COMPATIBLE_WORLDS:
            raise(Exception('Error: unknown or uncompatible world \"' + world + '\" for environnement round_bot'))
        
        if world == 'rb1':

            self.action_meaning = {
            0 : "MOVEFORWARD",
            1 : "STOP",
            2 : "ROTATERIGHT",
            3 : "ROTATELEFT",    
            }
        else:
            raise(Exception('Error: world '+ world +' should figure in code enumeration if elif..'))
            
        ## shared settings
        self.world = world
        self.model = round_bot_model.Model(world)
        self.winSize= list(winsize)
        try:
            self.window = pygletWindow.PygletWindow(self.model, width=winsize[0]/2, height=winsize[1]/2, caption='Round bot in '+world+' world', resizable=False, visible=False)
        except Exception as e:
            raise Exception("Error : could not load window for world : " + world)
        # observation are RGB images of rendered world      
        self.observation_space = spaces.Box(low=0, high=255, shape=[winsize[0], winsize[1], 3])
        self.action_space = spaces.Discrete(len(self.action_meaning))

    def get_action_meanings(self):
        return [self.action_meaning[i] for i in self.action_space]


    
