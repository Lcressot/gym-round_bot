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
class PygletWindow(pyglet.window.Window):
################################################################################################################################
    """
        Abstract class for rendering in a window with pyglet
    """

    def __init__(self, model, global_pov=None, perspective=True, interactive=False, focal=65.0, *args, **kwargs):
        super(PygletWindow, self).__init__(*args, **kwargs)
        """
        Parameters
        ----------
        - model : (Round_bot_model.Model) model linked to the window
        - global_pov : (Tuple(int, int, int) or Bool) Global point of view. If None, view is subjective.
            If True, automatic computing. Else set with Tuple(int, int, int)
        - perspective : (Bool) camera projection mode
        - interactive : (Bool) wether user can interact with window or not (use : take control of the robot for debug)
        - focal : (float) camera projective focal length
        - *args : Tuple args of parent Class pyglet.window.Window
        - **kwargs : Dict kwargs of parent Class pyglet.window.Window
        """
        # prevent user from instantiating directly this abstract class
        if type(self) is PygletWindow:
            raise NotImplementedError('Cannot instantiate this abstract class')

        # Instance of the model that handles the world.
        self.model = model

        # perspective or orthogonal projection
        self.perspective = perspective
        self.focal = focal
            
        # Global point of view : if None, view is subjective. If True, automatic computing
        if global_pov==True:
            # compute global_pov automatically
            global_pov = self.automatic_global_pov()

        elif global_pov: # if not True but not None
            self.ortho_width = global_pov[1]*np.tan(np.radians(focal/2.0)) 

        else: # if None
            if not perspective:
                print('Warning : no global_pov provided, setting perspective to True')
                self.perspective = True

        self.global_pov = global_pov

        # Wheter or not the user can interact with the window
        self.interactive = interactive          

        # Wether or not the window has its own thread
        self.threaded = False

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False        

        # Mapping from shown blocks to textures
        self.shown = dict()

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.texture_groups = dict()
        self.texture_groups['brick'] = TextureGroup(image.load(self.model.texture_paths['brick']).get_texture())
        self.texture_groups['robot'] = TextureGroup(image.load(self.model.texture_paths['robot']).get_texture())
        self.texture_groups['distractor'] = TextureGroup(image.load(self.model.texture_paths['distractors']).get_texture())
        self.texture_groups['sandbox'] = TextureGroup(image.load(self.model.texture_paths['brick']).get_texture())
        self.texture_groups['trigger_button'] = TextureGroup(image.load(self.model.texture_paths['brick']).get_texture())

        # add this window pointer to model
        self.model.add_window(self)

        # call private initialisation method
        self._init()

        # show all blocks
        self.model.show_visible_blocks(self)

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

        self._update(dt)
        # try update on all movable blocks
        for block in self.model.movable_blocks:
            try: # use of try except instead of if statement here for computational optimization
                self.shown[block].vertices = block.vertices        
            except KeyError:
                pass

    def step(self, dt):
        """
        Performs manually a drawing step
        """
        self.update(dt)
        self.on_draw()       
        if self.visible: 
            self.dispatch_events() # slows down rendering with a factor 10 on OSX
            self.flip()

    def _update(self, dt):
        """
        Private (protected) update of a window
        """
        raise NotImplemented

    def automatic_global_pov(self):
        """
        Sets up the global_pov automatically
        """
        self.perspective = False
        self.ortho_width = max(self.model.world_info['width']/2,self.model.world_info['depth']/2)
        return (0, self.ortho_width/np.tan(np.radians(self.focal/2.0)), 0)

    def show_block(self, block):
        """ Add block the shown dict
        """
        if self._show_block(block): # decide whether to show the block or not depending on the window
            self.shown[block] = self.batch.add(24, GL_QUADS, self.texture_groups[block.block_type],
                ('v3f/static', block.vertices),
                ('t2f/static', list(block.texture))
                )   

    def _show_block(self, block):
        """
            Private Boolean function for deciding whether to show a block or not 
        """ 
        raise NotImplemented

    def hide_block(self, block):
        """ Remove block from shown dict
        """
        self.shown.pop(block)

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
        return copy.deepcopy(nparr) # important to copy returned np.arrays !
   
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
            glOrtho(self.ortho_width, -self.ortho_width, self.ortho_width, -self.ortho_width ,0.1, self.global_pov[1]+5)
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
        self.switch_to() # set opengl context to this window
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.batch.draw()
        
        self._on_draw()
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def _on_draw(self):
        """
        Class private on_draw method
        """
        raise NotImplemented

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    def setup_fog(self):
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
        glFogf(GL_FOG_START, 0.0)
        glFogf(GL_FOG_END, 15.0)


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
        #self.setup_fog()
        self.switch_to() # set opengl context to this window

    def multiview_render(self, xzangles, as_line=False):
        """
        Parameters
        ----------
        - xzangles : List(float) list of angles representing subjective view rotation in plane xOz (positives to negatives)
        - as_line : (Bool) Wheter to return a line shaped image or not
        
        Returns
        -------
        A simple fusion of subjective views with given angles, used to widen the field of view

        Note : this function doesn't perform any model updates ! It must be done before
        """        
        nviews = len(xzangles)
        multiview_rnd = np.zeros([self.height, self.width, 3], dtype=np.uint8)
        w = int(self.width/nviews)

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
            multiview_rnd[:,i*w:(i+1)*w,:] = rnd
        # convert to uint8
        #multiview_rnd = multiview_rnd.astype(np.uint8)
        return multiview_rnd if not as_line else np.reshape(multiview_rnd,[1,self.width*self.height*3])

    def switch_pov(self):
        """
        Switches point of view between subjective and global
        """
        if not self.global_pov:
            self.global_pov = self.automatic_global_pov()
        else :
            self.global_pov = None
            self.perspective = True


################################################################################################################################
class MainWindow(PygletWindow):
################################################################################################################################
    """
        Class of main windows:
    """

    def __init__(self, model, global_pov=None, perspective=True, interactive=False, focal=65.0, *args, **kwargs):
        """
        Parameters
        ----------
        see parent Class PygletWindow __init__ parameters
        """
        super(MainWindow, self).__init__(model, global_pov, perspective, interactive, focal, *args, **kwargs)

        # set of windows following this one
        self.followers = set()

    def _init(self):
        """
        Private (protected) initialiation of a MainWindow object
        """
        return
        

    def start(self):
        """
        Starts window thread and set a callback on given function
        """
        # schedule calls on 
        # if callback:
        #     pyglet.clock.schedule_interval(callback, 1.0 / ticks_per_sec, 1)
        self.threaded = True
        pyglet.app.run()

    def _update(self, dt, m=1):
        """ 
        Private (protected) update of a window

        Parameters
        ----------
        - dt : (float) The change in time since the last call.
        - m : (int) subdisivions of step

        """
        # only main window can call for model update
        for _ in range(m):
            self.model.update(dt / m)
        # update following windows :
        for w in self.followers:
            w.step(dt)

    def _on_draw(self):
        """
        Class private on_draw method
        """
        return

    def add_follower(self, secondary_window):
        """
        adds a following window
        """
        self.followers.add(secondary_window)
        secondary_window.follow(self)

    def remove_follower(self, secondary_window):
        """
        removes a following window
        """
        if secondary_window not in self.followers:
            raise KeyError('the provided window was not part of the main window following windows')
        else:
            self.followers.remove(secondary_window)

    def _show_block(self, block):
        """
            Private Boolean function for deciding whether to show a block or not 
        """ 
        # only show visible blocks except start and reward
        # Note: robot block is too small to appear in the subjective view so showing it is not a problem
        if block.block_type in ['start','reward']:
            return False
        else:
            return block.visible 

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(PygletWindow, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive 


    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when a mouse button is pressed. See pyglet docs for button amd modifier mappings.

        Parameters
        ----------
        - x, y : (int) The coordinates of the mouse click. Always center of the screen if the mouse is captured.
        - button : (int) Number representing mouse button that was clicked. 1 = left button, 4 = right button.
        - modifiers : (int) Number representing any modifying keys that were pressed when the mouse button was clicked.
        """
        if not self.interactive or not self.threaded:
            return
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        - x, y : (int) The coordinates of the mouse click. Always center of the screen if the mouse is captured.
        - dx, dy : (float) The movement of the mouse.
        """
        # TODO : correct the y rotation to a mixed y,z rotation
        if self.exclusive and self.model.flying:
            m = 0.15
            self.model.change_robot_rotation(dx * m, dy * m)
            

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        - symbol : (int) Number representing the key that was pressed.
        - modifiers : (int) Number representing any modifying keys that were pressed.

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
        - symbol : (int) Number representing the key that was pressed.
        - modifiers : (int) Number representing any modifying keys that were pressed.
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


    def on_close(self):
        """
        When user closes window
        """
        for w in self.followers:
            w.on_close()
        super(MainWindow, self).on_close()




################################################################################################################################
class SecondaryWindow(PygletWindow):
################################################################################################################################
    """
        Class of secondary windows : used to observe model but don't interact with it
    """

    def __init__(self, model, global_pov=None, perspective=True, focal=65.0, *args, **kwargs):
        self.message = ''
         # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18, x=10, y=kwargs['height'] - 10, 
                                        anchor_x='left', anchor_y='top', color=(255, 255, 255, 255))    
        super(SecondaryWindow, self).__init__(model=model, global_pov=global_pov, perspective=perspective, interactive=False, focal=focal, *args, **kwargs)

    def _init(self):
        """
        Private (protected) initialiation of a SeondaryWindow object
        """
        self.main_window = None
        self.texture_groups['start'] = TextureGroup(image.load(self.model.texture_paths['visualisation']).get_texture())
        self.texture_groups['reward'] = self.texture_groups['start']  
        # show start areas
        for sa in self.model.start_areas:
            self.show_block(sa)      

    def _update(self, dt):
        """
        Private (protected) update of a SeondaryWindow object
        """
        return

    def _on_draw(self):
        """
        Class private on_draw method
        """
        self.set_2d()
        # draw some information on label
        self.draw_label(self.message)

    def draw_label(self, label_text):
        """ Draw the label in the top left of the screen.
        """
        self.label.text = label_text        
        self.label.draw()

    def follow(self, main_window):
        """
        A secondary has to follow a main window
        """
        self.main_window = main_window

    def on_close(self):
        """
        When user closes window
        """
        # only close main window (and thus application) if it is not visible
        if not self.main_window.visible:
            # first, remove this window from main_window followers list to avoid recursion of on_close function
            self.main_window.followers.remove(self)
            # then call on_close
            self.main_window.on_close()
        super(SecondaryWindow, self).on_close()

    def _show_block(self, block):
        """
            Private Boolean function for deciding whether to show a block or not 
        """ 
        # show visible blocks
        return block.visible

    def switch_pov(self):
        """
        Cannot switch point of view between subjective and global in a secondary_window
        """
        pass
