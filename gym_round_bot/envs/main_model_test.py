#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018
""" 

from __future__ import division

import sys

#import round_bot_py
import round_bot_model
import pygletWindow


if __name__ == '__main__':

    world = 'rb1_blocks'
    #world = 'rb1'
    winsize=[300,300]
    model = round_bot_model.Model(world)
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
		visible=True
	)

    secwindow = pygletWindow.SecondaryWindow(
        model,
        global_pov=(0,20,0),
        #global_pov=None,
        perspective=False,        
        width=winsize[0],
        height=winsize[1],
        caption='Observation window '+world,
        visible=True
    )

    window.add_follower(secwindow)
    window.start()
