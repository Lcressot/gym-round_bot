#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018
    code started from : https://github.com/fogleman/Minecraft
""" 

import math
import numpy as np
from sys import platform
import copy

import scipy.misc

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse


"""
    This file defines the environnement's window and renderer
"""
################################################################################################################################
class RoundBotWindow(pyglet.window.Window):
################################################################################################################################
    """
        Abstract class for rendering in a window with pyglet
    """

    def __init__(self, model, global_pov=None, perspective=True, interactive=False, focal=65.0, *args, **kwargs):
        super(RoundBotWindow, self).__init__(*args, **kwargs)
        """
        Parameters
        ----------
        - model : (Round_bot_model.Model) Model linked to the window
        - global_pov : (Tuple(int, int, int) or Bool) Global point of view. If None, view is subjective.
            If True, automatic computing. Else set with Tuple(int, int, int)
        - perspective : (Bool) camera projection mode
        - interactive : (Bool) wether user can interact with window or not (use : take control of the robot for debug)
        - focal : (float) camera projective focal length
        - *args : (tuple) args of parent Class pyglet.window.Window
        - **kwargs : (dict) kwargs of parent Class pyglet.window.Window
        """
        # prevent user from instantiating directly this abstract class
        if type(self) is RoundBotWindow:
            raise NotImplementedError('Cannot instantiate this abstract class')

        # Instance of the model that handles the world.
        self.model = model
        # perspective or orthogonal projection
        #self.perspective = perspective
        #self.focal = self.current_focal = focal

        #self.global_pov = global_pov
        # Wheter or not the user can interact with the window
        #self.interactive = interactive
        # Wether or not the window has its own thread
        #self.threaded = False
        # Whether or not the window exclusively captures the mouse.
        #self.exclusive = False
        # Mapping from shown blocks to textures
        #self.shown = dict()
        # A Batch is a collection of vertex lists for batched rendering.
        #self.batch = pyglet.graphics.Batch()
        # A TextureGroup manages an OpenGL texture.
        self.texture_groups = dict()
        # brick texture group
        self.texture_groups['brick'] = TextureGroup(image.load(self.model.texture_paths['brick']).get_texture())
        self.texture_groups['sandbox'] = TextureGroup(image.load(self.model.texture_paths['brick']).get_texture())
        self.texture_groups['trigger_button'] = TextureGroup(image.load(self.model.texture_paths['brick']).get_texture())

        # visualisation texture group
        self.texture_groups['start'] = TextureGroup(image.load(self.model.texture_paths['visualisation']).get_texture())
        self.texture_groups['reward'] = TextureGroup(image.load(self.model.texture_paths['visualisation']).get_texture())

        # other texture groups
        self.texture_groups['distractor'] = TextureGroup(image.load(self.model.texture_paths['distractors']).get_texture())
        self.texture_groups['robot'] = TextureGroup(image.load(self.model.texture_paths['robot']).get_texture())

        # set persepctive rendering aspect ratio (usefull to change for multiview render)
        #self.aspect_ratio = self.width / float(self.height)
        # add this window pointer to model
        #self.model.add_window(self)
        # call private initialisation method
        #self._init()
        # show all blocks
        #self.model.show_visible_blocks(self)
        # set up opengl
        self.setup_gl()
        # render first frame
        self.on_draw()

    def _init(self):
        """
        Private (protected) initialiation of a window
        """
        raise NotImplemented

    def update(self, dt):
        pass

    def step(self, dt):
        """
        Performs manually a drawing step
        """
        pass
        #self.update(dt)
        #self.on_draw()
        #if self.visible:
        #    self.dispatch_events() # slows down rendering with a factor 10 on OSX
        #    self.flip()


    def get_image(self,reshape=True):
        """
        Return a screenshot of the window
        """
        #return pyglet.image.get_buffer_manager().get_color_buffer()
        # read pixel data from opengl buffer
        #data = (GLubyte * (3 * self.width * self.height))(0)
        #glReadPixels(0, 0, self.width, self.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
        data = (GLubyte * (3 * self.width * self.height))(0)
        glReadPixels(0, 0, self.width, self.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
        # convert to numpy array
        nparr = np.fromstring(data,dtype=np.uint8)        
        if reshape:
            # reshape as image
            nparr=nparr.reshape(self.width,self.height,3)
        else:
            # reshape as line vector
            nparr=nparr.reshape(1,self.width*self.height*3)
        return copy.copy(nparr) # important to copy returned np.arrays !


    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        #self.switch_to() # set opengl context to this window
        self.clear()
        data = (GLubyte * (3 * self.width * self.height))(0)
        glReadPixels(0, 0, self.width, self.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
        for i in range(3 * self.width * self.height):
            print(i, data[i])
        #self.set_3d()
        #glColor3d(1, 1, 1)
        #self.batch.draw()

        #self._on_draw()

        #glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def setup_gl(self):
        """ Basic OpenGL configuration.

        """
        # Set the color of 'clear', i.e. the sky, in rgba.
        glClearColor(0.2, 0.2, 0.2, 1)
        # Enable culling (not rendering) of back-facing facets -- facets that aren't
        # visible to you.
        #glEnable(GL_CULL_FACE)

        # Set the texture minification/magnification function to GL_NEAREST (nearest
        # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
        # 'is generally faster than GL_LINEAR, but it can produce textured images
        # with sharper edges because the transition between texture elements is not
        # as smooth.'


################################################################################################################################
class MainWindow(RoundBotWindow):
################################################################################################################################
    """
        Class of main windows:
    """

    def __init__(self, model, *args, **kwargs):
        """
        Parameters
        ----------
        see parent Class RoundBotWindow __init__ parameters
        """
        super(MainWindow, self).__init__(model, *args, **kwargs)

        # set of windows following this one

    def _init(self):
        """
        Private (protected) initialiation of a MainWindow object
        """
        return

    def _update(self, dt, m=1):
        pass

    def _on_draw(self):
        """
        Class private on_draw method
        """
        return


    def on_close(self):
        """
        When user closes window
        """
        exit()