#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR CNRS/UPMC
    02/2018
    code started from : https://github.com/fogleman/Minecraft
""" 

import random
import time
import math
from gym_round_bot.envs import round_bot_worlds
import numpy as np

"""
    This file defines the environnement's Model (also Block class)
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


class Block(object):
    """
    Parent class for block objects
    """
    def __init__(self, position, rotation, dimensions, texture, visible=True, ghost=False, collision_reward=0.0, movable=False):
        """
        Parameters
        ----------
        - position : (np.array) x,y,z position of center
        - rotation : (np.array) rx,ry,rz rotation of vertices in absolute axis
        - dimensions : (np.array) dimensions of block (depending on its type)
        - texture : (list(float)) The coordinates of the texture squares. Use `tex_coords()` to generate.       
        - visible : (Bool) True if the block is visible. Collision will be detected even if not visible
        - ghost : (Bool) True if block can be gone by, collision will still be detected
        - collision_reward : (float) the reward returned at collision
        """
        self.movable = True # needed for allowing initialization moves
        self._make_block(position, dimensions, rotation) # sets self._position, self._dimensions, self._rotation
        self.movable = movable # now set self.movable to its value
        self.texture = texture        
        self.visible = visible
        self.isGhost = ghost
        # return reward when collided
        self.collision_reward = collision_reward
        self._init() # custom initilization

    def _init(self):
        self.block_type = 'block'

    @property
    def position(self):
        return self._position
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
        return self._rotation
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
        self.translate( position - self.position )

    def rotate(self,rotation):
        """Rotate vertices around x, y, z axis
            WARNING : block must be centered around origin, if not rx,ry and rz will become wrong values
        """
        if not self.movable:
            raise Exception('Cannot rotate not movable Block')
        Rx,Ry,Rz = rotation_matrices(*self.rotation)        
        R = np.matmul( Rx, np.matmul(Ry,Rz) )
        self._vertices = np.transpose(  np.dot(R, np.transpose(self._vertices))  )
        self._rotation = (self.rotation+rotation)%360.0

    def translate_and_rotate_to(self,offset_position, rotation):
        """
        Translate and rotate to given values (absolute and not relative transforms)
        """
        if not self.movable:
            raise Exception('Cannot set new position to not movable Block')
        self._make_block(offset_position, self.dimensions, rotation) # easier to recreate vertices form scratch
        


class Cube(Block):
    """
    Cubic block (dimensions are the same)
    """
    def __init__(self,position, rotation, size, texture, visible, ghost, collision_reward, movable=False):
        """
        parameters:
        ----------
        - size (int)
        """
        self.size = size
        super(Cube,self).__init__( position, rotation, np.ones(3)*size, texture, visible, ghost, collision_reward, movable=False)

    def cube_vertices(x_off, y_off, z_off, w, rx=0, ry=0, rz=0):
        """ Return the vertices of the cube at position x, y, z with size w.
            y is up
        """        
        return self.block_vertices(x_off, y_off, z_off, w, w, w, rx, ry, rz) 


class FlatBlock(Block):
    """
    Class for flat blocks, i.e with a 0 depth
    """

    def __init__(self,position, rotation, dimensions, texture, visible, ghost, collision_reward, movable=False):
        """
        parameters:
        ----------
        - dimensions (np.array(float) of len 2)
        """
        assert(len(dimensions)==2)
        super(FlatBlock,self).__init__( position, rotation, dimensions, texture, visible, ghost, collision_reward, movable=False)

    def _init(self):
        self.block_type = 'flat'

    @staticmethod
    def block_vertices(dimensions, position=np.zeros(3)):
        """ Return a np array of the vertices of the block centered on (x,y,z) with no rotation,
            and with size w h
            Note : y axis is up-down, (x,z) is the ground plane
        """
        w2=dimensions[0]/2.0; h2=dimensions[1]/2.0;
        x=position[0]; y=position[1]; z=position[2]
        return np.array([ [x-w2, y+h2, z], [x+w2, y+h2, z], [x-w2, y-h2, z], [x+w2, y-h2, z] ])

    @staticmethod
    def tex_coords(face):
        """ Return a list of the texture squares for the only face ot eh Flat Block.
        """
        return Block.tex_coord(*face)
   
class BrickBlock(Block):
    """
    BrickBlock are visible, not ghost blocks
    """
    def __init__(self, position, rotation, dimensions, texture, collision_reward=0.0):
        super(BrickBlock,self).__init__(position, rotation, dimensions, texture, visible=True, ghost=False, collision_reward=collision_reward, movable=True)
    def _init(self):
        self.block_type = 'brick'     

class RobotBlock(Block):
    """
    RobotBlock are movable blocks
    """
    def __init__(self, position, rotation, dimensions, texture, visible=True, ghost=False, collision_reward=0.0):
        super(RobotBlock,self).__init__(position, rotation, dimensions, texture, visible, ghost, collision_reward=collision_reward, movable=True)
    def _init(self):
        self.block_type = 'robot'

class StartBlock(Block):
    """
    StartBlock are not visible and ghost, but are visible in secondary windows
    """
    def __init__(self, position, rotation, dimensions, texture, collision_reward=0.0, movable=False):
        super(StartBlock,self).__init__(position, rotation, dimensions, texture, visible=False, ghost=True, collision_reward=collision_reward, movable=True)

    def _init(self):
        self.block_type = 'start'

class RewardBlock(Block):
    """
    RewardBlock are not visible and ghost blocks
    """
    def __init__(self, position, rotation, dimensions, texture, collision_reward=0.0, movable=False):
        super(RewardBlock,self).__init__(position, rotation, dimensions, texture, visible=False, ghost=True, collision_reward=collision_reward, movable=True)
    
    def _init(self):
        self.block_type = 'reward'


##########################################################################################################################
##########################################################################################################################
class Model(object):

    def __init__(self, world='rb1', texture='minecraft', random_start_pos=True, random_start_rot=False):
        """

        Class for round bot model. This class should play the model role of MVC structure,
        and should not deal with the rendering and the windowing (see class PygletWindow)
        or the controlling (see class RoundBotEnv)

        Parameters 
        ----------
        - world (str) : the name of the world to load. Worlds are defined in module round_bot_worlds
        - texture (str) : the name of the texture to be applied on blocks
        - random_start_pos (Bool) : wether the robot position is randomly sampled inside world's starting areas at reset or not.
        - random_start_rot (Bool) : wether the robot rotation is randomly sampled at reset or not.

        """

        # reference to windows
        self.windows = set()
        
        # A set of all blocks
        self.bricks = set()

        # A set of movable blocks
        self.movable = set()

        # set of starting areas:
        self.start_areas  = set()
    
        # whether to start randomly in starting_areas or always at the same initial position
        self.random_start_pos = random_start_pos
        # whether to rotation should be randomly chosen or not in reset()
        self.random_start_rot = random_start_rot

        self.ticks_per_sec = 60

        # default speed values
        self.walking_speed = 10
        self.initial_walking = 10
        self.flying_speed = 15
        
        self.world_info = None
        self.texture_paths = None # used for rendering with window
        self.start_position, self.start_rotation, self.start_strafe = None,None,None
        # maximum absolute possible reward in model, used for normalization
        self.max_reward=0.0

        # load world        
        self.load_world(world, texture)

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
            # sample x and z cooridinates
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
            self.robot_rotation[0] = random.random()*360  # only x component is randomly sampled                       

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = self.start_strafe

        self.flying = False   
        self.collided = False     

    def add_block(self, components, texture=None, block_type='brick', visible=True, ghost=False, collision_reward=0.0):
        """ Add a block to the model depending on its type

        Parameters
        ----------
        same as Block.__init__        
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
            block = BrickBlock( position, rotation, dimensions, texture, collision_reward )
            self.bricks.add( block )
        elif block_type=='robot':
            block = RobotBlock( position, rotation, dimensions, texture, collision_reward )
            self.robot_block = block
        elif block_type=='start':
            block = StartBlock( position, rotation, dimensions, texture, collision_reward )
            self.start_areas.add(block)
        elif block_type=='reward':
            block = RewardBlock( position, rotation, dimensions, texture, collision_reward )
            self.bricks.add( block ) # add reward blocks to bricks to detect collisions

        if block.movable:
            self.movable.add(block)

        # update max_reward value
        self.max_reward = max(self.max_reward, abs(block.collision_reward))

    def remove_block(self, block):
        """ Remove the block
        """        
        self.hide_block(block)

        if block.movable:
            self.movable.remove(block)
            
        if not block==self.robot_block:
            self.bricks.remove(block)
        else:
            del self.robot_block
        
   
    def show_block(self, block, window):
        """ Show the block in given window
        """
        window.show_block(block)
        # the window object decides whether to actually show the block or not
        # depending on the block type, its option visible and so on

    def show_all_bricks(self, window):
        """ Show all blocks at once
        """
        for block in self.bricks:
            self.show_block(block, window)
    

    def hide_block(self, block):
        """ Hide the block . Hiding does not remove the
        block from the world.
        """
        for w in self.windows:
            w.hide_block(block)
        

    # def get_sight_vector(self):
    #     """ Returns the current line of sight vector indicating the direction
    #     the player is looking.
    #     """
    
    #     x, y = self.robot_rotation
    #     # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
    #     # is 1 __en looking ahead parallel to the ground and 0 when looking
    #     # straight up or down.
    #     m = math.cos(math.radians(y))
    #     # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
    #     # looking straight up.
    #     dy = math.sin(math.radians(y))
    #     dx = math.cos(math.radians(x - 90)) * m
    #     dz = math.sin(math.radians(x - 90)) * m
    #     return (dx, dy, dz)

    def get_motion_vector(self):
        """
        Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        - vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

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
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def change_robot_rotation(self,dx,dy):
        """ Change robot rotation
        """
        x, y = self.robot_rotation
        # add dx dy and set to [-180 180]
        x,y = (x+dx +180.0)%360.0 -180.0, (y+dy +180.0)%360.0 -180.0
        self.robot_rotation = [ x, y ]

    def change_robot_position(self,dx,dy,dz):
        """ Change robot position (translate it)
        """
        x,y,z = self.robot_position
        self.robot_position = [ x+dx, y+dy, z+dz ]


    def update(self, dt):
        """
        This is where most of the motion logic lives

        Parameters
        ----------
        - dt (float): The change in time since the last call.
        """
        # walking
        speed = self.walking_speed if not self.flying else self.flying_speed
        
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d

        # collisions
        x, y, z = self.robot_position
        new_position = (x + dx, y + dy, z + dz)

        self.collided = self.collide(new_position)
        if not self.collided:
            self.robot_position = new_position

        # update robot's block
        # but don't add it in shown dict because this block is not show in all windows using the model      
        rx,ry = self.robot_rotation
        x, y, z = self.robot_position
        # TODO : rectify this strange rotation parametrization
        self.robot_block.translate_and_rotate_to( np.array([x,y,z]), np.array([-ry,-rx,0.0]) )


    def collide(self, new_position):
        """ Checks to see if the cylindric robot at the given new x,y,z
        position with given diamter and height
        is colliding with any blocks in the world.

        Parameter
        --------
        - new_position : new position of robot to check

        Returns
        -------
        - (Bool) collided
        """
        
        # iterate over blocks and check for collision :
        # TODO : improve collision result for sliding on walls
        # TODO : improve to integer diagonal walls
        # TODO : optimize with walls and floors (x2) or with quadtree
        x,y,z = new_position
        self.current_reward=0.0
        robot_width, robot_height, robot_depth  = self.robot_block.dimensions
        for brick in self.bricks:
            xcol,ycol,zcol = False,False,False
            xb,yb,zb = brick.position
            w,h,d = brick.dimensions
            if abs(x-xb) <  (w+robot_width)/2.0:
                xcol = True
            if abs(z-zb) <  (d+robot_depth)/2.0:
                zcol = True
            if abs(y-yb) <  (h+robot_height)/2.0 :
                ycol = True
            if xcol and zcol and ycol:
                # get block collision reward to be used in RL envs, then return True
                self.current_reward += brick.collision_reward
                if not brick.isGhost: # detect collision only if block is not ghost
                    return True        

        return False


    def load_world(self, world, texture):
        """ Loads the world passed as string parameter

        """
        if world == 'rb1':
            texture_paths, world_info = round_bot_worlds.build_rb1_world(self, texture)
        elif world == 'rb1_1wall':
            texture_paths, world_info = round_bot_worlds.build_rb1_1wall_world(self, texture)
        else:
            raise(Exception('Error: unknown world : ' + world))

        self.world_info = world_info
        self.texture_paths = texture_paths
        self.start_position = self.robot_block.position
        rx,ry,_ = self.robot_block.rotation
        # Note: ry,rx -> x,y cause x is (Oxz) wheras rx is rotation around x, same for y and ry
        self.start_rotation = (ry,rx)
        self.start_strafe = [0.0,0.0] # start with a null strafe
            
    def position_observation(self):
        """
        returns
        -------
        np.array : array of arrays of every position and rotation of movable blocks ( no need to compute non movable )
        """
        arrays=[]
        for b in self.movable:
            arrays.append(list(b.position)+list(b.rotation))
        return np.array(arrays)


