# gym-round_bot

This repository gives a robotic simulation environment compatible with OpenAI gym. The simulation is a simple round bot driving in a simple maze-type world with walls. It is desgined as follows :

### Model :
round_bot_model.py

The 3D model of the simulation (no OpenGl) which loads the world's points and moves the robot, dealing with collisions. This module should not include rendering code (see MVC code structure) because visualisation is done in the pygletWindow module.

### Window :
pygletWindow.py

+ A class inherited from python Pyglet library for rendering 3D scenes (given by the model) with OpenGL. Interaction with user is possible (to control the model's robot) if the window is set to visible and interactive. If the window is visible and interactive, control the robot for debugging your world or have fun with tab (to enter control mode), and ZSQD AE and mouse for direction and rotation.
+ Set the view to subjective with global_pov=None or set it to global with for instance global_pov=(0,40,0)
+ If you set global_pov, you can set perspective to False to render in orthogonal mode

### Worlds :
round_bot_worlds.py

This module defines functions for loading/building simulated worlds : each function loads/builds a different world. Later, this module could be replaced by a function for writting/reading worlds information in files.

### Main_model_test
main_model_test.py

This script shows how to run a simple simulation (without Open AI Gym) simply by constructing a model and a visible interactive window.

### Controller :
round_bot_controller.py

This module defines a class for controlling the robot of a model. Given an action number, it can return its string meaning or perform the corresponding action in the model. For the Theta controller, you can set the speed and teta rotation of the robot, but do no set a to high speed because you could go through walls !

### Open AI gym environment :
round_bot_env.py

This module defines the OpenAI gym compatible environment using a model and a window (in this case the window is only used for rendering and is non interactive nor visible, and has not its main thread. You can set it to visible but it slows down computations by a factor 10)


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

# Use

Here is a simple code for using the environment :
```Python
import gym
import gym_round_bot

# create environment
env = gym.make('RoundBot-v0')
world = 'rb1' # the world to load
winsize=[100,80] # the size of window for rendering

controller={'name':'Theta','dteta':45,'speed':5}

# load the environment (if not called, default is world='rb1',winsize=[80,60], controller={'name':'Theta','dteta':20,'speed':10}), global_pov = None, perppective=True )
env.unwrapped.load(world='rb1',winsize=winsize, controller=controller, global_pov = (0,20,0)), perppective=False)

# perform a step
ob, reward, done, _ = env.step(action)


# perform steps
while(True):
    ob, reward, done, _ = env.step(0)
    # render to screen if needed
    env.render()
```
