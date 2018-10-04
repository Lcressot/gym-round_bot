#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018

    Small script for testing and understanding the model and windows (no gym env involved here)
""" 

import round_bot_model
import pygletWindow


if __name__ == '__main__':

    world_name = 'square_1wall'
    #world_name = 'square'
    world = {'name':world_name,'size':[20,20]}
    winsize=[600,600]
    #model = round_bot_model.Model(world,'colours',distractors=True)
    #model = round_bot_model.Model(world,'graffiti', sandboxes=True)
    model = round_bot_model.Model(world,'graffiti')
    window = pygletWindow.MainWindow(
    	model,
		#global_pov=(0,20,0),
		global_pov=None,
		perspective=True,
		interactive=True,
		width=winsize[0],
		height=winsize[1],
		caption='Round bot in '+world['name']+' world',
		resizable=False,
		visible=True,
	)

    secwindow = pygletWindow.SecondaryWindow(
        model,
        global_pov=True,
        #global_pov=None,
        perspective=False,        
        width=winsize[0],
        height=winsize[1],
        caption='Observation window '+world['name'],
        visible=True
    )

    window.add_follower(secwindow)
    window.start()
