# gym-round_bot

OpenAI gym environment for robotic simulation. The simulation is a simple round bot driving in a 3D maze-type world with walls. It is compatible with both Python 2 and 3.

<img src="https://github.com/Lcressot/gym-round_bot/blob/master/RoundBot.png" width="450" align="center">

### Table of contents
1. [Modules](#modules)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [Credits](#credits)
6. [License](#license)


# Modules <a name="modules"></a>

### Model : <a name="model"></a>
round_bot_model.py

The 3D model of the simulation (no OpenGl) which loads the world's points and moves the robot, dealing with collisions. This module should not include rendering code (see MVC code structure) because visualization is done in the round_bot_window module.

### Window : <a name="window"></a>
round_bot_window.py

+ A class inherited from python Pyglet library for rendering 3D scenes (given by the model) with OpenGL. Interaction with the user is possible (to control the model's robot) if the window is set to visible and interactive. If the window is visible and interactive, control the robot for debugging your world or have fun with tab (to enter control mode), and ZSQD AE and mouse for direction and rotation.
+ Set the view to subjective with global_pov=None or set it to global with for instance global_pov=(0,40,0). Use global_pov=True for automatic global_pov computing.
+ If you set global_pov, you can set perspective to False to render in orthogonal mode.
+ Use a MainWindow for rendering and optionally a SecondaryWindow object for monitoring the training/testing

### Worlds : <a name="worlds"></a>
round_bot_worlds.py

This module defines functions for loading/building simulated worlds : each function loads/builds a different world. Later, this module could be replaced by a function for writing/reading worlds information in files.

### Testing the model <a name="testmodel"></a>
test_model.py

This script shows how to run a simple simulation (without Open AI Gym) simply by constructing a model and a visible interactive window.

### Controller : <a name="controller"></a>
round_bot_controller.py

This module defines a class for controlling the robot of a model. Given an action, it can return its string meaning or perform the corresponding action in the model.
Controllers are subclass of either ContinuousController or DiscreteController, which are subclasses of the Controller abstract class.
Regarding the Discrete Theta controller, you can set the speed and teta rotation of the robot, but do no set a to high speed because you could go through walls ! Note that a speed of X means a displacement of X units per step in the room, it does not concern the computation speed of the software.

### OpenAI gym environment : <a name="gymenv"></a>
round_bot_env.py

This module defines the OpenAI gym compatible environment using a model and a window (in this case the window is only used for rendering and is non-interactive nor visible, and has not its main thread. You can set it to visible but it slows down computations by a factor 10)

### Testing the Env : <a name="testenv"></a>
test_env.py

This script provides a simple code for running a round bot gym environment


# Installation <a name="installation"></a>

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


# Usage <a name="usage"></a>

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
world = {'name':'square','size':[20,20]} # the world to load
obssize=[16,16] # the size of observations (rendering window)
winsize=[300,300] # the size of monitoring window (None if not wanted)
controller = rbc.make('Theta2',speed=1,dtheta=15, xzrange=[1,1], thetarange=1) # the robot controller
                
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

## Usage on a server :

This environment uses OpenGL to render 3D objects and thus needs a graphic card to run.
You may try to run it either way on a server: in this case please post your solution or report an issue.

# Contributing <a name="contributing"></a>

## To do list <a name="todo"></a>
+ add other movable object that can be pushed by the robot, or doors that can open (see TriggerButton Blocks)
+ add pytest tests
+ correct the robot rotation in free flying mode with global point of view (debug mode) : it is not correct, the robot block needs to be rotated in all direction and not only around y axis (not very important issue). This correction may apply to any other rotating block. See methods round_bot_model.Block.update and round_bot_window.RoundBotWindow.set_3D.
+ find why we need to put a +1 to the number of sub motions in round_bot_model.Model.collide to avoid wall crossing, and also find why this trick doesn't work for very high speeds
+ find a better way to modify aspect_ratio and focal in round_bot_window.Window.multi_view_render() to make render look good

## Code documentation <a name="documentation"></a>
Please use this documentation format to document the new functions (and change the old which are not conform yet):
```Python

def function(param_1, .. param_n):

    """
    function concise description

    Parameters: (if any)
    ----------
    - param_1 : (param_1_type) description of param_1
    
    ...

    - param_n : (param_n_type) description of param_1

    Returns (if any)
    -------
    - returned_var1 : (returned_var1_type) description of returned_var1

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

    Parameters:
    ----------
    - n : (int) size of fibonacci sequence to compute

    Returns 
    -------
    List(int) : Fibonnaci sequence of length n

    """
```
Please also use this format to document new modules and classes.


# Credits <a name="credits"></a>

Main author : Loic Cressot

Code started from : https://github.com/fogleman/Minecraft

# License <a name="license"></a>

This repo is under MIT license

