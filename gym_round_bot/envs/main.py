from __future__ import division

import sys

#import round_bot_py
import round_bot_model as tb_model
import pygletWindow


if __name__ == '__main__':

    world = 'rb1'
    winsize=[300,300]
    model = tb_model.Model(world)
    window = pygletWindow.PygletWindow(model, global_pov=(0,40,0), perspective=False, interactive=True, width=winsize[0], height=winsize[1], caption='Round bot in '+world+' world', resizable=False, visible=True)
    window.start()
    # for i in range(1,3):
    #     window.step(0.1)
    #     window.debug_render()
