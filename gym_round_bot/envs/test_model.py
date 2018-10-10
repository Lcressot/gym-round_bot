#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018

    Small script for testing and understanding the model and windows (no gym env involved here)
""" 

import round_bot_model
import round_bot_window


if __name__ == '__main__':

    world_name = 'square_1wall'
    #world_name = 'square'
    world = {'name':world_name,'size':[20,20]}
    winsize=[600,600]
    model = round_bot_model.Model(world,'graffiti')
    window = round_bot_window.MainWindow(
    	model,
		#global_pov=(0,20,0),
		global_pov=True,
		perspective=True,
		interactive=True,
		width=winsize[0],
		height=winsize[1],
		caption='Round bot in '+world['name']+' world',
		resizable=False,
		visible=True,
	)

    secwindow = round_bot_window.SecondaryWindow(
        model,
        global_pov=True,#None,
        perspective=False,        
        width=winsize[0],
        height=winsize[1],
        caption='Observation window '+world['name'],
        visible=True
    )

    window.add_follower(secwindow)
    window.start()
