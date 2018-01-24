from __future__ import division

import sys

#import round_bot_py
import round_bot_model as tb_model
import pygletWindow
import thread


if __name__ == '__main__':

	world = 'rb1'
	winsize=[800,600]
	model = tb_model.Model(world)
	window = pygletWindow.PygletWindow(model, interactive=True, width=winsize[0], height=winsize[1], caption='Round bot in '+world+' world', resizable=True, visible=True)
	window.start()

	