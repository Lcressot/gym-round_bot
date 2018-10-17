#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018
    code started from : https://github.com/fogleman/Minecraft
""" 

import random
import copy
import time
import math
from gym_round_bot.envs import round_bot_worlds
import numpy as np

"""
    This file defines the environment's Model (also Block class)
"""

def rotation_matrices(rx,ry,rz):
    """
    Return numpy rotation matrices along x,y,z    
    """
    rx,ry,rz = np.radians(rx), np.radians(ry), np.radians(rz)
    c, s = np.cos(rx), np.sin(rx)
    Rx=np.matrix([[1.0,0.0,0.0],[0.0, c, -s],[0.0, s, c  ]])
    c, s = np.cos(ry), np.sin(ry)
    Ry=np.matrix([[c,0.0,s],[0.0, 1, 0.0],[-s, 0.0, c ]])
    c, s = np.cos(rz), np.sin(rz)
    Rz=np.matrix([[c, -s, 0.0],[s, c, 0.0 ],[0.0, 0.0, 1.0 ]])
    return Rx, Ry, Rz





################################################################################################################################################
################################################################################################################################################
class Block(object):
    """
    Parent class for block objects
    """
    def __init__(self, position, dimensions, rotation, texture, visible=True, crossable=False, collision_reward=0.0, movable=False, linked_block=None, friction=1.0):
        """
        Parameters: 
        ----------
        - position : (np.array) x,y,z position of center
        - dimensions : (np.array) dimensions of block (depending on its type)
        - rotation : (np.array) rx,ry,rz rotation of vertices in absolute axis
        - texture : (list(float)) The coordinates of the texture squares. Use `tex_coords()` to generate.       
        - visible : (Bool) True if the block is visible. Collision will be detected even if not visible
        - crossable : (Bool) True if block can be gone by, collision will still be detected
        - collision_reward : (float) the reward returned at collision
        - linked_block (Block) : a block to follow if any, the bounding box position relative to the linked block will stay constant
            TODO : improve update to take account of linked_block rotations too
        - friction : friction coefficient of block
        """
        self.movable = True # needed for allowing initialization moves
        self._make_block(np.array(position), np.array(dimensions), np.array(rotation)) # sets self._position, self._dimensions, self._rotation
        self.movable = movable # now set self.movable to its value
        self.texture = texture
        self.visible = visible
        self.crossable = crossable
        self.inCollision = False # whether block is currently in a collision
        if not friction > 0.0 and friction <= 1.0:
            raise ValueError('Block friction must be in range ]0,1] ')
        self.friction = friction

        # return reward when collided
        self.collision_reward = collision_reward

        self._linked_block = linked_block
        self._relative_position = self._position - linked_block._position if linked_block else None

        self._init() # custom initialization

    def _init(self):
        self.block_type = 'block'

    def update_to_relative_position(self):
        """ update the block's position to its relative position to its linked_block if any
        """
        if self._linked_block:
           self._position = self._linked_block._position + self._relative_position

    # Properties are to be used externally to the class because they are computationally more costfull than direct call to _attributes
    @property
    def position(self):
        return copy.deepcopy(self._position)
    @position.setter
    def position(self, position):
        # sets the block to a position
        self.translateTo(position) # and translate the vertices
    @property
    def x(self):
        return self._position[0]
    @property
    def y(self):
        return self._position[1]
    @property
    def z(self):
        return self._position[2]
      
    @property
    def rotation(self):
        return copy.deepcopy(self._rotation)
    @property
    def rx(self):
        return self._rotation[0]
    @property
    def ry(self):
        return self._rotation[1]        
    @property
    def rz(self):
        return self._rotation[2]

    @property
    def dimensions(self):
        return self._dimensions
    @property
    def w(self):
        return self._dimensions[0]
    @property
    def h(self):
        return self._dimensions[1]
    @property
    def d(self):
        return self._dimensions[2]

    @property
    def components(self):
        return self._position, self._dimensions, self._rotation, 
   
    @property
    def vertices(self):
        """ Return vertices as python list of coordinates
        """
        return self._vertices.flatten().tolist()[0]

    @staticmethod
    def block_vertices(dimensions, position=np.zeros(3)):
        """ Return a np array of the vertices of the block centered on (x,y,z) with no rotation,
            and with size w d h
            Note : y axis is up-down, (x,z) is the ground plane
        """
        w2=dimensions[0]/2.0; h2=dimensions[1]/2.0; d2=dimensions[2]/2.0
        x=position[0]; y=position[1]; z=position[2]
        return np.array([
            [x-w2, y+h2, z-d2], [x-w2, y+h2, z+d2], [x+w2, y+h2, z+d2], [x+w2, y+h2, z-d2],   # top
            [x-w2, y-h2, z-d2], [x+w2, y-h2, z-d2], [x+w2, y-h2, z+d2], [x-w2, y-h2, z+d2],   # bottom
            [x-w2, y-h2, z-d2], [x-w2, y-h2, z+d2], [x-w2, y+h2, z+d2], [x-w2, y+h2, z-d2],   # left
            [x+w2, y-h2, z+d2], [x+w2, y-h2, z-d2], [x+w2, y+h2, z-d2], [x+w2, y+h2, z+d2],   # right
            [x-w2, y-h2, z+d2], [x+w2, y-h2, z+d2], [x+w2, y+h2, z+d2], [x-w2, y+h2, z+d2],   # front
            [x+w2, y-h2, z-d2], [x-w2, y-h2, z-d2], [x-w2, y+h2, z-d2], [x+w2, y+h2, z-d2]    # back
            ])

    def _make_block(self, position, dimensions, rotation=np.zeros(3)):
        """ Return a np array of the vertices of the cube at position x_off, y_off, z_off
            with size w d h and rotation rx ry rz around x y z axis.
            Note : y axis is up-down, (x,z) is the ground plane
        """
        self._position = np.zeros(3)
        # first create a block centered around (0,0,0)
        self._dimensions = dimensions
        self._vertices = self.block_vertices(dimensions)
        # then rotate it along x, y, z axis
        self._rotation = rotation
        self.rotate(rotation)
        # finally translate it of x_off, y_off, z_off
        self.translate(position)

    @staticmethod
    def tex_coord(x, y, n=4):
        """ Return the bounding vertices of the texture square.
        """
        m = 1.0 / n
        dx = x * m
        dy = y * m
        return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

    @staticmethod
    def tex_coords(top, bottom, side):
        """ Return a list of the texture squares for the top, bottom and side.
        """
        top = Block.tex_coord(*top)
        bottom = Block.tex_coord(*bottom)
        side = Block.tex_coord(*side)
        result = []
        result.extend(top)
        result.extend(bottom)
        result.extend(side * 4)
        return result
    
    def translate(self,vector):
        """Translates vertices of vector
        """
        if not self.movable:
            raise Exception('Cannot translate not movable Block')
        self._vertices += vector
        self._position += vector

    def translateTo(self,position):
        """Translates all vertices to center them on position
        """
        if not self.movable:
            raise Exception('Cannot translate not movable Block')
        self.translate( position - self._position )


    def rotate(self,rotation):
        """Rotate vertices around x, y, z axis
            WARNING : block must be centered around origin, if not rx,ry and rz will become wrong values
        """
        if not self.movable:
            raise Exception('Cannot rotate not movable Block')
        Rx,Ry,Rz = rotation_matrices(*self._rotation)        
        R = np.matmul( Rx, np.matmul(Ry,Rz) )
        self._vertices = np.transpose(  np.dot(R, np.transpose(self._vertices))  )
        self._rotation = (self._rotation+rotation)%360.0

    def translate_and_rotate_to(self,offset_position, rotation):
        """
        Translate and rotate to given values (absolute and not relative transforms)
        """
        if not self.movable:
            raise Exception('Cannot set new position to not movable Block')
        self._make_block(offset_position, self._dimensions, rotation) # easier to recreate vertices form scratch
        
    def collide(self, inCollision):
        """
        Called when block is collided are not collided anymore

        parameter:
        ----------
        inCollision (bool) : True if block is collided, false if it is not
        """
        self.inCollision = inCollision

################################################################################################
class Cube(Block):
    """
    Cubic block (dimensions are the same)
    """
    def __init__(self,position, rotation, size, texture, visible=True, crossable=False, collision_reward=0.0, movable=False):
        """
        Parameters:
        ----------
        - size (int)
        """
        self.size = size
        super(Cube,self).__init__( position, rotation, np.ones(3)*size, texture, visible, crossable, collision_reward, movable=movable)

    def cube_vertices(x_off, y_off, z_off, w, rx=0, ry=0, rz=0):
        """ Return the vertices of the cube at position x, y, z with size w.
            y is up
        """        
        return self.block_vertices(x_off, y_off, z_off, w, w, w, rx, ry, rz) 


################################################################################################
class FlatBlock(Block):
    """
    Class for flat blocks, i.e with a 0 depth. It has only 4 vertices and 1 face (instead of 8 vertices and 6 faces)
    """
    def _init(self):
        if not sum(dimensions==0.0)==1:
            raise ValueError('FlatBlock must have exactly one null dimension')
        # cut texture list to size one if it has been set to longer
        self.texture = [self.texture[0]]
        self.block_type = 'flat'
        # null dimension has eventually to be replaced by a small value for now
        # TODO : allow really flat blocks (with one unique face)
        dimensions[dimensions==0] = 0.05

    # @staticmethod
    # def block_vertices(dimensions, position=np.zeros(3)):
    #     """ Return a np array of the vertices of the block centered on (x,y,z) with no rotation,
    #         and with size w h
    #         Note : y axis is up-down, (x,z) is the ground plane
    #     """
    #     w2,h2,d2=dimensions/2.0
    #     x,y,z=position
    #     if w2==0.0:
    #         return np.array([ [x, y+h2, z+d2], [x, y+h2, z+d2], [x, y-h2, z-d2], [x, y-h2, z-d2] ])
    #     elif h2==0.0:
    #         return np.array([ [x-w2, y, z+d2], [x+w2, y, z+d2], [x-w2, y, z-d2], [x+w2, y, z-d2] ])
    #     elif d2==0.0:
    #         return np.array([ [x-w2, y+h2, z], [x+w2, y+h2, z], [x-w2, y-h2, z], [x+w2, y-h2, z] ])
    #     else:
    #         raise Exception('FlatBlock should have exactly one null dimension')

    # @staticmethod
    # def tex_coords(face):
    #     """ Return a list of the texture squares for the only face ot eh Flat Block.
    #     """
    #     return Block.tex_coord(*face)

################################################################################################   
class BoundingBoxBlock(Block):
    """ BoundingBoxBlock are crossable
    """
    def __init__(self, position, dimensions, rotation, collision_reward=0.0, movable=False, linked_block=None, visible=False):

        super(BoundingBoxBlock,self).__init__(position, dimensions, rotation, texture=None,
                                              visible=visible, crossable=True, collision_reward=collision_reward,
                                              movable=movable, linked_block=linked_block)
    def _init(self):
        self.block_type = 'boundingBox'

################################################################################################
class BrickBlock(Block):
    """ BrickBlock are visible, not crossable blocks
    """
    def __init__(self, position, dimensions, rotation, texture, collision_reward=0.0):
        super(BrickBlock,self).__init__(position, dimensions, rotation, texture,
                                        visible=True, crossable=False, collision_reward=collision_reward, movable=True)
    def _init(self):
        self.block_type = 'brick'     

################################################################################################
class RobotBlock(Block):
    """ RobotBlock are movable blocks, shown only when view is global (hidden in subjective view)
    """
    def __init__(self, position, dimensions, rotation, texture, visible=True, crossable=False, collision_reward=0.0):
        super(RobotBlock,self).__init__(position, dimensions, rotation, texture,
                                        visible, crossable, collision_reward=collision_reward, movable=True)
    def _init(self):
        self.block_type = 'robot'

################################################################################################
class StartBlock(BoundingBoxBlock):
    """ StartBlock are only visible in secondary windows and are crossable
    """
    def __init__(self, position, dimensions, rotation, texture, collision_reward=0.0, movable=False):
        super(StartBlock,self).__init__(position, dimensions, rotation, collision_reward=0.0, movable=movable, visible=True)
        self.texture = texture

    def _init(self):
        self.block_type = 'start'

################################################################################################
class RewardBlock(BoundingBoxBlock):
    """ RewardBlock are only visible in secondary windows and crossable blocks
    """
    def __init__(self, position, dimensions, rotation, texture, collision_reward=0.0, movable=False):
        super(RewardBlock,self).__init__(position, dimensions, rotation, collision_reward=collision_reward, movable=movable, visible=True)
        self.texture = texture

    def _init(self):
        self.block_type = 'reward'

################################################################################################
class DistractorBlock(Block):
    """ DistractorBlock are blocks that move around randomly to distract the observer. They are crossable, visible and movable.
        They can move within a given bounding box, bouncing against the walls and sometimes changing directions
    """
    def __init__(self, boundingBox, dimensions, rotation, texture, collision_reward=0.0, speed=1.0, change_dir_frequency=0.01):
        """
        Parameters:
        -----------
        - no position because it is initialized at the center of the boundingBox
        - boundingBox (BoundingBoxBlock) : bounding box inside which the 
        - speed (float) : displacement speed of distractor
        - change_dir_frequency (float) : frequency of direction changing when moving
        - other *args : see Block.__init__
        """
        super(DistractorBlock,self).__init__(boundingBox.position, dimensions, rotation, texture,
                                             visible=True, crossable=True, collision_reward=collision_reward, movable=True)
        self._boundingBox = boundingBox
        self._degrees_of_freedom = (self._dimensions < self._boundingBox.dimensions) # axis on which the distractor can move inside the bounding box
        if self._boundingBox is not None and not any(self._degrees_of_freedom):
            raise ValueError('DistractorBlock\'s boundingBox must have at least one bigger dimension to allow displacement')
        self._change_direction_frequency = change_dir_frequency # frequency of changing direction
        self._absolute_speed = speed #(float)
        self._relative_position = np.zeros(3) # relative_position to bounding box (which can move)
        self._speed = np.zeros(3) # speed of displacement within bounding box (vector)
        # initialize moving speed
        self.change_direction()

    def _init(self):
        self.block_type = 'distractor'

    def change_direction(self):
        """ causes the distractor to change its moving direction within its constrained axis of degrees of freedom
        """
        self._speed = np.random.random_sample((3,))*self._degrees_of_freedom.astype(float) # take a random direction of speed in constrained axis
        self._speed *= self._absolute_speed / np.sqrt(np.sum(self._speed**2)) # set speed vector length so absolute_speed value

    def move_in_bounding_box(self):
        """ Tell the distractor to move within its bounding box of displacement
        """
        # check if change direction
        if np.random.random_sample() < self._change_direction_frequency:
            self.change_direction()
        # move and check collision (collision means out of bounding box on freedom axis)
        new_position = self._position + self._speed
        collision = (np.abs(new_position - self._boundingBox.position) > (self._boundingBox.dimensions - self._dimensions)/2.0)*self._degrees_of_freedom
        if any( collision ):
           # collision detected, speed is inversed in the collision axis
           self._speed[collision] *= -1
        else:
            # if no collision, validate new position
            self.position = new_position

################################################################################################        
class FlatDistractorBlock(DistractorBlock, FlatBlock):
    """ child class FlatBlock and DistractorBlock
    """
    def __init__(self, boundingBox, dimensions, rotation, texture, collision_reward=0.0, speed=1.0, change_dir_frequency=0.01):
        super(FlatDistractorBlock,self).__init__(boundingBox=boundingBox, dimensions=dimensions, rotation=rotation,
                                                 texture=texture, collision_reward=collision_reward, speed=speed,
                                                 change_dir_frequency=change_dir_frequency)


################################################################################################
class SandBoxBlock(FlatBlock):
    """
    SandBox Blocks are flat, crossable and have a low friction coefficient
    """
    def __init__(self, position, dimensions, rotation, texture, collision_reward=0.0, movable=False, linked_block=None, friction=0.5, visible=True):
        if friction == 1.0:
            raise ValueError('SandBoxBlock must have a friction < 1.0, i.e that slows down the robot')
        super(SandBoxBlock, self).__init__(position=position, dimensions=dimensions, rotation=rotation, texture=texture,
                                           visible=visible, crossable=True, collision_reward=collision_reward, movable=movable,
                                           linked_block=linked_block, friction=friction)
    def _init(self):
        self.block_type = 'sandbox'


################################################################################################
class TriggerButtonBlock(BoundingBoxBlock):
    """
    TriggerButtonBlock are crossable, visible, and trigger a function call when crossed
    """
    def __init__(self, position, dimensions, rotation, texture, collision_reward=0.0, movable=False):
        super(TriggerButtonBlock,self).__init__(position, dimensions, rotation, collision_reward=collision_reward, movable=movable, visible=True)
        self.texture = texture
        # the self.trigger_function will be called when the block is crossed, but it needs to be initialized before
        def default_trigger(*args, **kwargs):
            raise Exception('trigger_function has not been initialized')
        self.trigger_function = default_trigger

    def trigger(self, *args, **kwargs):
        self.trigger_function(*args, **kwargs)

    def _init(self):
        self.block_type = 'trigger_button'

    def collide(self, inCollision):
        """
        Called when block is collided

        Parameter:
        ----------
        inCollision (bool) : True if block is collided, false if it is not
        """
        # trigger the button only if the block is newly under collision
        if not self.inCollision and inCollision :
            self.trigger()
        self.inCollision = inCollision














##################################################################################################################################################
##################################################################################################################################################
class Model(object):

    def __init__(self,world={'name':'square','size':[20,20]},texture='minecraft',random_start_pos=True,random_start_rot=False,distractors=False,sandboxes=False,trigger_button=False):
        """

        Class for round bot model. This class should play the model role of MVC structure,
        and should not deal with the rendering and the windowing (see class RoundBotWindow)
        or the controlling (see class RoundBotEnv)

        Parameters 
        ----------
        - world : (dict) world to load with a least name entry. Worlds are defined in module round_bot_worlds
        - texture : (str) the name of the texture to be applied on blocks
        - random_start_pos : (Bool) whether the robot position is randomly sampled inside world's starting areas at reset or not.
        - random_start_rot : (Bool) whether the robot rotation is randomly sampled at reset or not.
        - distractors : (Bool) whether to add visual distractors on walls or not
        - sandoxes : (Bool) whether to add visual distractors on walls or not
        - trigger_button : (Bool) whether to add a trigger button
        """
        # reference to windows
        self.windows = set()
        # A set of all visible blocks
        self.visible_blocks = set()
        # A set of all collision blocks
        self.collision_blocks = set()
        # A set of  blocks currently under collision
        self.under_collision_blocks = set()
        # A set of movable blocks
        self.movable_blocks = set()
        # set of starting areas:
        self.start_areas  = set()
        # set of distractor blocks :
        self.distractors = set()
        # whether to start randomly in starting_areas or always at the same initial position
        self.random_start_pos = random_start_pos
        # whether to rotation should be randomly chosen or not in reset()
        self.random_start_rot = random_start_rot

        self.ticks_per_sec = 60
        # default speed values
        self.rolling_speed = 10
        self.current_friction = 1.0 # friction of the current material on which the robot is standing (0 < friction <= 1)
        # Note : this friction is a pourcentage of speed reduction, not a physical friction coefficient between two materials
        
        self.world_info = None
        self.texture_paths = None # used for rendering with window
        self.start_position, self.start_rotation, self.start_strafe = None,None,None
        # for continuous actions
        self.speed_continuous = np.array([0, 0], dtype=float)
        self.acceleration = None
        # maximum absolute possible reward in model, used for normalization
        self.max_reward=0.0
        # load world        
        self.load_world(world, texture, distractors, sandboxes, trigger_button)
        self.flying, self.collided, self.current_reward = None, None, None
        # reset first time
        self.reset()

    @property
    def robot_diameter(self):
        return self.robot_block.w/2.0

    @property
    def robot_height(self):
        return self.robot_block.h

    def add_window(self, window):
        self.windows.add(window)
        
    def reset(self):
        """
        Current x, y, z position in the world, specified with floats. Note
        that, perhaps unlike in math class, the y-axis is the vertical axis.
        """
        if self.random_start_pos:           
            start_area = random.choice( list(self.start_areas) )
            # sample x and z coordinates
            self.robot_position = [0,]*3
            self.robot_position[0] = random.random()*(start_area.w-2*self.robot_diameter) + start_area.x - (start_area.w-2*self.robot_diameter)/2.0
            self.robot_position[2] = random.random()*(start_area.d-2*self.robot_diameter) + start_area.z - (start_area.d-2*self.robot_diameter)/2.0
            self.robot_position[1] = start_area.y

        else:
            self.robot_position = self.start_position

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.robot_rotation = list(self.start_rotation)

        if self.random_start_rot:
            self.robot_rotation[0] = random.random()*360-180  # only x component is randomly sampled
        else:
            self.robot_rotation = self.start_rotation

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = self.start_strafe
        self.current_friction = 1.0

        self.flying = False   
        self.collided = False     

    def add_block(self, components, texture=None, block_type='brick', visible=True, crossable=False, collision_reward=0.0, boundingBox=None, speed=1.):
        """ Add a block to the model depending on its type

        Parameters :
        -----------   
        - same as Block.__init__     

        Returns:
        -------
        - the added block
        """        
        if len(components)==9:
            position = np.array(list(components[0:3]))
            dimensions = np.array(list(components[3:6]))
            rotation = np.array(list(components[6:9]))
        elif len(components)==3:
            position, dimensions, rotation = components
            position = np.array(position)
            dimensions = np.array(position)
            rotation = np.array(position)

        if block_type=='brick':
            block = BrickBlock( position=position, dimensions=dimensions, rotation=rotation, texture=texture, collision_reward=collision_reward )
            self.collision_blocks.add( block )
        elif block_type=='robot':
            block = RobotBlock( position=position, dimensions=dimensions, rotation=rotation, texture=texture, collision_reward=collision_reward )
            self.robot_block = block
        elif block_type=='start':
            block = StartBlock( position=position, dimensions=dimensions, rotation=rotation, texture=texture, collision_reward=collision_reward )
            self.start_areas.add(block)
        elif block_type=='sandbox':
            block = SandBoxBlock( position=position, dimensions=dimensions, rotation=rotation, texture=texture, collision_reward=collision_reward )
            self.collision_blocks.add(block)
        elif block_type=='reward':
            block = RewardBlock( position=position, dimensions=dimensions, rotation=rotation, texture=texture, collision_reward=collision_reward )
            self.collision_blocks.add( block )
        elif block_type == 'distractor':
            block = DistractorBlock( boundingBox=boundingBox, dimensions=dimensions, rotation=rotation,
                                      texture=texture, collision_reward=collision_reward, speed=speed) # warning no position for this block !
            self.distractors.add(block)
        elif block_type == 'flat_distractor':
            block = FlatDistractorBlock( boundingBox=boundingBox, dimensions=dimensions, rotation=rotation,
                                      texture=texture, collision_reward=collision_reward, speed=speed) # warning no position for this block !
            self.distractors.add(block)
        elif block_type=='trigger_button':
            block = TriggerButtonBlock( position=position, dimensions=dimensions, rotation=rotation, texture=texture, collision_reward=collision_reward )
            self.collision_blocks.add( block )
            # set the trigger function to switch_pov for now
            block.trigger_function = self.switch_pov
        else:
            raise ValueError('Unknown block_type : ' + block_type)

        if block.movable:
            self.movable_blocks.add(block)

        if block.visible:
            self.visible_blocks.add(block)

        # update max_reward value
        self.max_reward = max(self.max_reward, abs(block.collision_reward))

        return block       

    def remove_block(self, block):
        """ Remove the block
        """        
        self.hide_block(block) # hide it
        # try to remove it from all sets
        def silent_try_func(func, element):
            try:
                func(element)
            except:
                pass
        silent_try_func( self.visible_blocks.remove, block )
        silent_try_func( self.collision_blocks.remove, block )
        silent_try_func( self.movable_blocks.remove, block )
        silent_try_func( self.start_areas .remove, block )
        silent_try_func( self.distractors.remove, block )
        
        if block is self.robot_block:
            del self.robot_block
   
    def show_block(self, block, window):
        """ Show the block in given window
        """
        window.show_block(block)
        # the window object decides whether to actually show the block or not
        # depending on the block type, its option visible and so on

    def show_visible_blocks(self, window):
        """ Show all visible blocks at once
        """
        for block in self.visible_blocks:
            self.show_block(block, window)
    

    def hide_block(self, block):
        """ Hide the block . Hiding does not remove the
        block from the world.
        """
        for w in self.windows:
            w.hide_block(block)
        

    def get_motion_vector(self):
        """
        Returns the current motion vector indicating the velocity of the player
        """
        if any(self.strafe):
            x, y = self.robot_rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1  
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1            
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = dx = dz = 0.0
        return np.array([dx,dy,dz])

    def change_robot_rotation(self,dx,dy):
        """ Change robot rotation
        """
        x, y = self.robot_rotation
        # add dx dy and set to [-180 180]
        self.robot_rotation = (self.robot_rotation+np.array([dx,dy])+180.0)%360.0 -180.0

    def change_robot_position(self,dx,dy,dz):
        """ Change robot position (translate it)
        """
        x,y,z = self.robot_position
        self.robot_position += np.array([dx,dy,dz])

    def update(self, dt):
        """
        This is where most of the motion logic lives

        Parameters
        ----------
        - dt (float): The change in time since the last call.
        """

        if not self.acceleration :
            # ====Discrete actions====
            #### update robot position
            # walking
            speed = self.rolling_speed
            d = dt * speed * self.current_friction  # distance covered this tick.
            motion_vec = self.get_motion_vector()
            # New position in space, before accounting for gravity.
            motion_vec *= d

        else:
            #====Continuous actions====
            #### update robot position
            ## Derive positions
            acceleration = np.array(self.acceleration)
            motion_vec = self.speed_continuous * dt
            motion_vec = np.array([motion_vec[0], 0, motion_vec[1]])

            ## Derive speed
            self.speed_continuous = self.speed_continuous + acceleration * dt
        
        # compute new position and friction with collide if motion_vec is not null
        if any(motion_vec):
            self.collided = self.collide(motion_vec)
       
        # update robot's block
        x, y = self.robot_rotation
        # TODO : rectify this strange rotation parametrization
        self.robot_block.translate_and_rotate_to(self.robot_position, np.array([0.0,-x,0.0]))

        #### update distractors
        for d in self.distractors:
            d.move_in_bounding_box()


    def collide(self, motion_vector):
        """ Checks to see if the cylindric robot at the given new x,y,z position with given diameter and height
                is colliding with any blocks in the world.
            Also modify the current_friction value
        Parameter :
        ----------
        - new_position : new position of robot to check
        Returns
        -------
        - (np.array) overlap vector if any, and last overlaping dimension(s), else None
        """
        # iterate over blocks and check for collision :
        # TODO : improve to integer diagonal walls
        # TODO : optimize with walls and floors (x2) or with quadtree
        self.current_reward=0.0
        self.current_friction = 1.0
        collided=False

        # compute the number of sub_motions to compute to check collisions and avoid wall crossing
        sub_motions = np.max(np.ceil(np.abs(motion_vector)/self.robot_block.dimensions))
        # perform sub_motions to avoid wall crossing when speed is high
        for m in range(1,int(sub_motions)+1):
            # compute sub motion vector
            sub_motion_vector = (m/sub_motions)*motion_vector

            for block in self.collision_blocks:
                new_overlap = (block.dimensions+self.robot_block.dimensions)/2.0 - np.abs(self.robot_position+sub_motion_vector - block.position)
                if all( new_overlap > 0):
                    try:
                        block.collide(True) # signal to the block it has been collided
                    except NotImplementedError:
                        pass
                    # get block collision reward to be used in RL envs
                    if block.collision_reward < 0:
                        self.current_reward = min(self.current_reward, block.collision_reward) # if negative reward is min 
                    elif self.current_reward>=0 : # negative beats positive
                        self.current_reward += block.collision_reward # if positive, reward sums up
                    # update current friction ratio
                    self.current_friction = min(self.current_friction, block.friction)
                    # react to collision only if block is not crossable
                    if not block.crossable:
                        # old overlap is needed to know on which dimensions the problematic overlapping has been done in the last move
                        old_overlap = (block.dimensions+self.robot_block.dimensions)/2.0 - np.abs(self.robot_position - block.position)
                        #  update motion_vector to cancel this collision
                        sub_motion_vector -= new_overlap * (old_overlap<0) * np.sign(motion_vector) *1.1
                        collided = True
                    else:
                        self.under_collision_blocks.add(block) # add this block to the set of block currently under collision
                else:
                    try:
                        self.under_collision_blocks.remove(block)
                        block.collide(False) # signal to the block it is not collided anymore
                    except KeyError:
                        pass
            # end sub motions if collided
            if collided:
                break

        # update robot position with sub motion vector which is motion vector if there was no collision
        self.robot_position += sub_motion_vector # update
        return collided


    def load_world(self, world, texture, distractors, sandboxes, trigger_button):
        """ Loads the world passed as string parameter
        """
        world_size = None

        if world['name'] == 'square':            
            try:
                world_size = world['size']
            except KeyError:
                world_size = [20,20]
            texture_paths, world_info = round_bot_worlds.build_square_world(self, texture=texture, distractors=distractors,
                                                                         sandboxes=sandboxes, trigger_button=trigger_button,
                                                                         width=world_size[0], depth=world_size[1])
        elif world['name'] == 'square_1wall':
            try:
                world_size = world['size']
            except KeyError:
                world_size = [20,20]
            texture_paths, world_info = round_bot_worlds.build_square_1wall_world(self, texture=texture, distractors=distractors,
                                                                         sandboxes=sandboxes, trigger_button=trigger_button,
                                                                         width=world_size[0], depth=world_size[1])
        else:
            raise(Exception('Error: unknown world : ' + world['name']))

        self.world_info = world_info
        self.texture_paths = texture_paths
        self.start_position = self.robot_block.position
        rx,ry,_ = self.robot_block.rotation
        self.start_rotation = (rx,ry)
        self.start_strafe = [0.0,0.0] # start with a null strafe
            
    def position_observation(self):
        """
        returns
        -------
        np.array : array of arrays of every position and rotation of movable blocks ( no need to compute non movable )
        """
        arrays=[]
        for b in self.movable_blocks:
            arrays.append(list(b.position)+list(b.rotation))
        return np.array(copy.deepcopy(arrays))
        #only robot block
        #return copy.deepcopy(np.reshape(np.concatenate( [self.robot_position, self.robot_rotation] ),[1,-1]) )

    def switch_pov(self):
        """
        Switches point of view between subjective and global in windows
        """
        for w in self.windows:
            w.switch_pov()
