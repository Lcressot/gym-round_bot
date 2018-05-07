#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018

    Small script for testing and understanding the model and windows (no gym env involved here)
""" 

import round_bot_model
import pygletWindow


if __name__ == '__main__':

    #world = 'rb1_1wall'
    world = 'rb1'
    winsize=[400,400]
    #model = round_bot_model.Model(world,'colours',distractors=True)
    model = round_bot_model.Model(world,'minecraft', sandboxes=True)
    window = pygletWindow.MainWindow(
    	model,
		#global_pov=(0,20,0),
		global_pov=None,
		perspective=True,
		interactive=True,
		width=winsize[0],
		height=winsize[1],
		caption='Round bot in '+world+' world',
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
        caption='Observation window '+world,
        visible=True
    )

    window.add_follower(secwindow)
    window.start()
