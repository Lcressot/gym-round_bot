# gym-round_bot

This repository gives a robotic simulation environment compatible with OpenAI gym. The simulation is a simple round bot driving in a simple maze-type world with walls. It is desgined as follows :

### Model :
round_bot_model.py

The 3D model of the simulation (no OpenGl) which loads the world's points and moves the robot, dealing with collisions. This module should not include rendering code (see MVC code structure) because visualisation is done in the pygletWindow module.

### Window :
pygletWindow.py

+ A class inherited from python Pyglet library for rendering 3D scenes (given by the model) with OpenGL. Interaction with user is possible (to control the model's robot) if the window is set to visible and interactive. If the window is visible and interactive, control the robot for debugging your world or have fun with tab (to enter control mode), and ZSQD AE and mouse for direction and rotation.
+ Set the view to subjective with global_pov=None or set it to global with for instance global_pov=(0,40,0). Use global_pov=True for automatic global_pov computing.
+ If you set global_pov, you can set perspective to False to render in orthogonal mode.
+ Use a MainWindow for rendering and optionnaly a SecondaryWindow object for monitoring the training/testing

### Worlds :
round_bot_worlds.py

This module defines functions for loading/building simulated worlds : each function loads/builds a different world. Later, this module could be replaced by a function for writting/reading worlds information in files.

### Test model
test_model.py

This script shows how to run a simple simulation (without Open AI Gym) simply by constructing a model and a visible interactive window.

### Controller :
round_bot_controller.py

This module defines a class for controlling the robot of a model. Given an action number, it can return its string meaning or perform the corresponding action in the model. For the Theta controller, you can set the speed and teta rotation of the robot, but do no set a to high speed because you could go through walls !

### Open AI gym environment :
round_bot_env.py

This module defines the OpenAI gym compatible environment using a model and a window (in this case the window is only used for rendering and is non interactive nor visible, and has not its main thread. You can set it to visible but it slows down computations by a factor 10)

### Test env
test_env.py

This script provides a simple code for running an round bot gym environment


# Installation

python 2:
```bash
cd gym-round_bot
pip install -e .
```
python 3:
```bash
cd gym-round_bot
pip3 install -e .
```

### Bug encountered on ubuntu when working with multiple environments: 
```bash
Error in `python3': malloc(): memory corruption:
```
To solve it:
```bash
sudo apt-get install libtcmalloc-minimal4
export LD_PRELOAD="/usr/lib/libtcmalloc_minimal.so.4"
```


# Use

Here is a simple code for using the environment (cf test_env.py ):
```Python
import gym
import gym_round_bot

# create environment
import gym
import gym_round_bot
from gym_round_bot.envs import round_bot_env
from gym_round_bot.envs import round_bot_controller as rbc

# set variables 
world = 'rb1' # the world to load
obssize=[16,16] # the size of observations (rendering window)
winsize=[300,300] # the size of monitoring window (None if not wanted)
controller = rbc.make('Theta2',speed=5,dtheta=15, xzrange=1, thetarange=1) # the robot controller
                
# set env metadata
round_bot_env.set_metadata(
        world=world,
        obssize=obssize,
        winsize=winsize,
        controller=controller,
   )
    
# create env 
env = gym.make('RoundBot-v0')

# need to be called at least once
env.reset() 

# perform steps
while(True):
	ob, reward, done, _ = env.step((0,0))
	# render to screen if needed
	env.render()
```

# Development

## TODO
# DEV
+ save used controller in main_agent_vs_environnement, then load it when necessary instead of rebuilding it
+ add continuous action possibility
+ add other movable object that can be pushed by the robot, or doors that can open
+ add buttons object than triggers events when pushed (collided)
+ add pytest tests

# BUGS
+ Cannot close window when it not interactive. It should be closable.
+ The robot y rotation in free flying mode for debug is not correct (not very important) see function PygletWindow.on_mouse_motion

## Code documentation
Please use this documentation format to document the new functions (and change the old which are not conform):
```Python

def function(param_1, .. param_n):

    """
    function concise description

    Parameters (if any)
    ----------
    - param_1 : (param_1_type) description of param_1
    
    ...

    - param_n : (param_n_type) description of param_1

    Returns (if any)
    -------
    return_type : return description

    Exceptions (if any)
    ----------
    - exception_type : description of exception

    Restrictions (if any)
    ------------
    - restriction : description of restriction of function use

    Side Effects (if any)
    ------------
    - side effect : description of side effect
    """
```
Example :
```Python

def fibonacci(n):

    """
    Computes fibonacci sequence

    Parameters
    ----------
    - n : (int) size of fibonacci sequence to compute

    Returns 
    -------
    List(int) : Fibonnaci sequence of length n

    """
```
Please also use this format to document new modules and classes.