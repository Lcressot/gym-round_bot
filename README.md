# gym-round_bot

This repository gives a robotic simulation environment compatible with OpenAI gym. The simulation is a simple round bot driving in a simple maze-type world with walls. It is desgined as follows :

### Model : round_bot_model.py
The 3D model of the simulation (no OpenGl) which loads the world's points and moves the robot, dealing with collisions. This module should not include rendering code (see MVC code structure) because visualisation is done in the pygletWindow module.

### Window : pygletWindow.py
A class inherited from python Pyglet library for rendering 3D scenes (given by the model) with OpenGL. Interaction with user is possible (to control the model's robot) if the window is set to visible and interactive. If the window is visible and interactive, control the robot for debugging your world or have fun with tab (to enter control mode), and ZSQD AE and mouse for direction and rotation.
Note that if you set the window to be visible, the computation time is multiplied by 10.

### Worlds : round_bot_worlds.py
This module defines functions for loading/building simulated worlds : each function loads/builds a different world. Later, this module could be replaced by a function for writting/reading worlds information in files.

### Main.py
This script shows how to run a simple simulation (without Open AI Gym) simply by constructing a model and a visible interactive window.

### Open AI gym environment : round_bot_env.py (IN CONSTRUCTION)
This module defines the OpenAI gym compatible environment using a model and a window (in this case the window is only used for rendering and is non interactive nor visible, and has not its main thread)


# Installation

```bash
cd gym-round_bot
pip install -e .
```

For now, you also need to copy the above text in gym/gym/envs/\_\_init\_\_.py :
```Python
register(
    id='RoundBot-v0',
    entry_point='gym_round_bot.envs:RoundBotEnv',
    max_episode_steps=200,
    reward_threshold=25.0,
)
```
You can set your own values for max_episode_steps and reward_treshold.

# Use

Here is a simple code for using the environment :
```Python
# create environment
env = gym.make('RoundBot-v0')
world = "rb1" # the world to load
winsize=[100,80] # the size of window for rendering

# load the environment (if not called, default is 'rb1',[80,60])
env.unwrapped.load(world,winsize)

# perform a step
ob, reward, done, _ = env.step(action)

# render to screen if needed
env.render()
```
