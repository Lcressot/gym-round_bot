import gym

from gym import error, spaces
from gym import utils
from gym.utils import seeding

try:
    #import round_bot_py
    import round_bot_model
    import pygletWindow
    import round_bot_controller    
except ImportError as e:
    # TODO : set dependencies for round_bot (pyglet)
    raise error.DependencyNotInstalled("{}. (HINT: you can install round_bot dependencies by running 'pip install gym[round_bot]'.)".format(e))

import numpy as np

#import logging 
#logger = logging.getLogger(__name__)

COMPATIBLE_WORLDS={ "rb1", # rectangle set, first person view, reward in top left corner
                    "rb1_blocks", # rectangle set, first person view, reward in top left corner, middle blocks
}

COMPATIBLE_CONTROLLERS ={ "Simple_ThetaSpeed", "Simple_XZ"
}

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
        self.winSize= None
        self.window = None
        self.observation_space = None
        self.action_space = None        
        self.current_observation = None
        self.controller = None        
        self.multiview = None
        self.load() #default world loaded
                

    def step(self, action):
        """
        Perform one step
        """
        reward = 0.0

        # perform action
        self.controller.step(action)
        
        # update
        if not self.multiview:
            self.window.step(0.1) # update with 1 second intervall
            # get observation
            self.current_observation = self.window.get_image(reshape=False)
        else:
            self.window.update(0.1) # update with 1 second intervall
            self.current_observation = self.window.multiview_render(self.multiview, as_line=True)

        # compute reward depending on the world
        if self.world == "rb1":                            
            # reward -1 if agent bumps into a wall
            if self.model.collided:
                reward = reward - 1.0
            # reward 1 if agent is in top right corner of the rectangle world with radius 0.3 * width
            x,y,z = self.model.robot_position
            w = self.model.world_info["width"]
            d = self.model.world_info["depth"]
            # check distance to bottom left
            if (x+(-w)/2.0)**2 + (z+(-d)/2.0)**2 < (0.3*min(w,d))**2:
                reward = reward + 1.0
            # reward 0 else                 

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
        self.current_observation = self.window.get_image(reshape=False)#get image as a numpy line
        return self.current_observation
        

    def render(self, mode='human', close=False):

        if mode == 'rgb_array':
            return self.current_observation
        elif mode == 'human':
            # this slows down rendering with a factor 10 !
            # TODO : show current observation on screen (potentially fusionned image, and not only last render !)
            if not self.window.visible:
                self.window.set_visible(True)
        elif mode == 'rgb_image':
            # reshape line array
            return np.reshape(self.current_observation, [self.winSize[0],self.winSize[1],3])
        else: 
            raise Exception('Unknown render mode: '+mode)


    def seed(self, seed=None):
        seed = seeding.np_random(seed)
        return [seed]

    def load(self,
            world='rb1',
            controller={"name":'Simple_ThetaSpeed',"dtheta":20,"speed":10},
            winsize=[80,60],
            global_pov=None,
            perspective=True,
            visible=False,
            multiview=None,
            focal=65.0,
            ):
        """
        Loads a world into environnement
        """
        if not world in COMPATIBLE_WORLDS:
            raise(Exception('Error: unknown or uncompatible world \"' + world + '\" for environnement round_bot'))
        
        if not "name" in controller or not controller["name"] in COMPATIBLE_CONTROLLERS:
            raise(Exception('Error: unknown or uncompatible controller \"' + str(controller) + '\" for environnement round_bot'))
                    
        ## shared settings
        self.world = world
        self.model = round_bot_model.Model(world)


        if controller["name"]=="Simple_ThetaSpeed":
            self.controller = round_bot_controller.Simple_ThetaSpeed_Controller(model=self.model, dtheta=controller["dtheta"],speed=controller["speed"])
            self.action_space = spaces.Discrete(len(self.controller.actions))

        elif controller["name"]=="Simple_XZ":
            xzrange=controller["xzrange"]
            self.controller = round_bot_controller.Simple_XZ_Controller(model=self.model, speed=controller["speed"], xzrange=xzrange)
            self.action_space = spaces.MultiDiscrete([2*xzrange+1,2*xzrange+1])
        
        self.winSize= list(winsize)
        #try:
        self.window = pygletWindow.PygletWindow(self.model,
                                                global_pov=global_pov,
                                                perspective = perspective,
                                                interactive=False,
                                                focal=focal,
                                                width=winsize[0],
                                                height=winsize[1],
                                                caption='Round bot in '+world+' world',
                                                resizable=False,
                                                visible=visible
                                                )
        # observation are RGB images of rendered world (as line arrays)
        self.observation_space = spaces.Box(low=0, high=255, shape=[1, winsize[0]*winsize[1]*3])

        self.multiview = multiview # if not None, observations will be fusion of subjective view with given relative xOz angles



    
