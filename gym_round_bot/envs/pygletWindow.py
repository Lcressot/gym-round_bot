#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018
    code started from : https://github.com/fogleman/Minecraft
""" 

import math
import numpy as np
from sys import platform

import scipy.misc

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse


"""
    This file defines the environnement's window and renderer
"""


class PygletWindow(pyglet.window.Window):

    def __init__(self, model, global_pov=None, perspective=True, interactive=False, focal=65.0, *args, **kwargs):
        super(PygletWindow, self).__init__(*args, **kwargs)

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.texture_groups = {'brick':None, 'robot':None}
        self.texture_groups['brick'] = TextureGroup(image.load(model.texture_paths['brick']).get_texture())
        self.texture_groups['robot'] = TextureGroup(image.load(model.texture_paths['robot']).get_texture())

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # Global point of view : if None, view is subjective
        self.global_pov = global_pov        
        if not global_pov:
            if not perspective:
                print('Warning : no global_pov provided, setting perspective to True')
                perspective = True
        else:
            self.ortho_width = self.global_pov[1]*np.tan(np.radians(focal/2.0)) 
        # perspective or orthogonal projection
        self.perspective = perspective
        self.focal = focal        

        # Wether or not the window has its own thread
        self.threaded = False

        # Wheter or not the user can interact with the window
        self.interactive = interactive        

        # Which sector the player is currently in.
        #self.sector = None

        # The crosshairs at the center of the screen.
        #self.reticle = None

        # Instance of the model that handles the world.
        self.model = model

        # set window pointer of model
        self.model.window = self

        # show all blocks
        self.model.show_all_bricks()
        if self.global_pov: # if global_pov, show robot's block
            self.model.show_robot=True
            self.show_block(self.model.robot_block)

    def show_block(self, block):
        """ Private implementation of the `show_block()` method.
        """
        # FIXME Maybe `add_indexed()` should be used instead
        self.model.shown[block] = self.batch.add(24, GL_QUADS, self.texture_groups[block.block_type],
            ('v3f/static', block.vertices),
            ('t2f/static', list(block.texture)))    

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(PygletWindow, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive   

    def update(self, dt, m=1):
        """ 
        Parameters
        ----------
        dt : float
            The change in time since the last call.
        m :  subdisivions of step

        """
        #self.model.process_queue()

        for _ in range(m):
            self.model.update(dt / m)

    def get_image(self,reshape=True):
        """
        Return a screenshot of the window
        """
        #return pyglet.image.get_buffer_manager().get_color_buffer()
        # read pixel data from opengl buffer
        data = ( GLubyte * (3*self.width*self.height) )(0)
        glReadPixels(0, 0, self.width, self.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
        # convert to numpy array
        nparr = np.fromstring(data,dtype=np.uint8)        
        if reshape:
            # reshape as image
            nparr=nparr.reshape(self.width,self.height,3)
        else:
            # reshape as line vector
            nparr=nparr.reshape(1,self.width*self.height*3)
        return nparr    

   
    def on_mouse_press(self, x, y, button, modifiers):
    #     """ Called when a mouse button is pressed. See pyglet docs for button
    #     amd modifier mappings.

    #     Parameters
    #     ----------
    #     x, y : int
    #         The coordinates of the mouse click. Always center of the screen if
    #         the mouse is captured.
    #     button : int
    #         Number representing mouse button that was clicked. 1 = left button,
    #         4 = right button.
    #     modifiers : int
    #         Number representing any modifying keys that were pressed when the
    #         mouse button was clicked.

    #     """
        if not self.interactive or not self.threaded:
            return
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive and self.model.flying:
            m = 0.15
            x, y = self.model.robot_rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y)) if not self.global_pov else 0.0
            self.model.robot_rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        # return if window is not interactive
        if not self.interactive or not self.threaded:
            return
        # allow to control robot for debug mode
        if self.model.flying:
            if symbol == key.Z:
                self.model.strafe[0] -= 1
            elif symbol == key.S: # same for qwerty  and azerty
                self.model.strafe[0] += 1
            elif symbol == key.Q:
                self.model.strafe[1] -= 1
            elif symbol == key.D: # same for qwerty and azerty
                self.model.strafe[1] += 1
            elif symbol == key.E:
                self.model.change_robot_rotation(10,0)
            elif symbol == key.A:
                self.model.change_robot_rotation(-10,0)            

        if symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            if not self.model.flying:
                # This call schedules the `update()` method to be called
                # TICKS_PER_SEC. This is the main game event loop.
                # if flying then the robot is controlled by the keyboard and mouse
                pyglet.clock.schedule_interval(self.update, 1.0 / self.model.ticks_per_sec)
            else:
                pyglet.clock.unschedule(self.update)
            
            self.model.flying = not self.model.flying

        

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        # return if window is not interactive
        if not self.interactive or not self.threaded:
            return
        # allow to control robot for debug mode
        if self.model.flying:
            if symbol == key.Z:
                self.model.strafe[0] += 1
            elif symbol == key.S: # same for qwerty  and azerty
                self.model.strafe[0] -= 1
            elif symbol == key.Q: 
                self.model.strafe[1] += 1
            elif symbol == key.D: # same for qwerty and azerty
                self.model.strafe[1] -= 1        


    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self, offset_xzangle=0.0):
        """ Configure OpenGL to draw in 3d.
            offset_xzangle : put offset to xOz angle, used for getting several views at each position and fusion them
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.perspective:
            gluPerspective(self.focal, width / float(height), 0.1, 60.0)
        else :
            # if not perspective, make orthogonal projection given the global_pov            
            glOrtho(self.ortho_width, -self.ortho_width, self.ortho_width, -self.ortho_width ,0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if self.global_pov:
            glRotatef(90, 45, 0, 0) # look down           
            x,y, z = self.global_pov
            glTranslatef(-x, -y, -z)
        else:
            x, y = self.model.robot_rotation
            glRotatef(x+offset_xzangle, 0, 1, 0)
            glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
            x,y, z = self.model.robot_position
            glTranslatef(-x, -y, -z)        

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.batch.draw()
        #self.draw_focused_block()
        # self.set_2d()
        # self.draw_label()
        #self.draw_reticle()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x,y, z = self.model.robot_position
        self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model.shown), len(self.model.textures))
        self.label.draw()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    def setup_fog():
        """ Configure the OpenGL fog properties.

        """
        # Enable fog. Fog 'blends a fog color with each rasterized pixel fragment's
        # post-texturing color.'
        glEnable(GL_FOG)
        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
        # Say we have no preference between rendering speed and quality.
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)
        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)


    def setup_gl(self):
        """ Basic OpenGL configuration.

        """
        # Set the color of 'clear', i.e. the sky, in rgba.
        glClearColor(0.2, 0.2, 0.2, 1)
        # Enable culling (not rendering) of back-facing facets -- facets that aren't
        # visible to you.
        glEnable(GL_CULL_FACE)
        # Set the texture minification/magnification function to GL_NEAREST (nearest
        # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
        # 'is generally faster than GL_LINEAR, but it can produce textured images
        # with sharper edges because the transition between texture elements is not
        # as smooth.'
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        #setup_fog()
        self.switch_to() # set opengl context to this window

    def start(self):#, callback=None, ticks_per_sec=20):
        """
            Starts window thread and set a callback on given function
        """
        # set up opengl
        self.setup_gl()
        # schedule calls on 
        # if callback:
        #     pyglet.clock.schedule_interval(callback, 1.0 / ticks_per_sec, 1)
        self.threaded = True
        pyglet.app.run()

    def step(self, dt):
        """
        Performs manually a drawing step
        """
        self.update(dt)
        self.on_draw()       
        if self.visible: 
            self.dispatch_events() # slows down rendering with a factor 10 on OSX
            self.flip()

    def multiview_render(self, xzangles, as_line=True):
        """
        xzangles : list of angles representing subjective view rotation in plane xOz (positives to negatives)
        as_line : Boolean for returning a line shaped image
        
        Returns a simple fusion of subjective views with given angles, used to widen the field of view

        Note : this function doesn't perform any model updates ! It must be done before
        """        
        nviews = len(xzangles)
        multiview_rnd = np.zeros([self.height, self.width, 3])
        w = self.width/nviews

        for i,xzangle in enumerate(xzangles):
            # render view with this xzangle as xz offset angle
            self.clear()
            self.set_3d(xzangle)
            glColor3d(1, 1, 1)
            self.batch.draw()            
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            # if self.visible: # slows down rendering with a factor 10 !
            #     self.dispatch_events()
            #     self.flip()
            rnd = self.get_image(reshape=True)
            # resize it (streching)
            rnd = scipy.misc.imresize(rnd, (self.height,w,3)) # warning imresize take x,y and not w,h !
            # insert it in multiview_rnd
            multiview_rnd[:,i*w:(i+1)*w,:] = 255-rnd # warning scipy has invert colors !            
            
        return multiview_rnd if not as_line else np.reshape(multiview_rnd,[1,self.width*self.height*3])


    def debug_render(self):
        """
        debug render
        """
        import matplotlib.pyplot as plt
        import numpy as np
        # data = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data().get_data('RGB',100)
        # a = np.fromstring(data,dtype=np.uint8)
        # print(len(a))
        # read pixel data from opengl buffer
        data = ( GLubyte * (3*self.width*self.height) )(0)
        glReadPixels(0, 0, self.width, self.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
        # convert to numpy array
        nparr = np.fromstring(data,dtype=np.uint8).reshape(100,100,3)
        plt.imshow(np.flipud(nparr), interpolation='nearest')
        plt.pause(1)
        #print(data)


