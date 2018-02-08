
import random
import time
import math
import round_bot_worlds
import numpy as np

"""
    This file defines the environnement's Model
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

    def __init__(self,components,texture,block_type, visible=True, ghost=False, collision_reward=0.0):
        """
        components : (x,y,z,w,h,d,rx,ry,rz) tuple of components for initialisation
        texture : list of len 3
                  The coordinates of the texture squares. Use `tex_coords()` to generate.       
        block_type : type of the block for later use
        visible : True if the block is visible. Collision will be detected even if not visible
        ghost : True if block can be gone by, collision will still be detected
        collision_reward : the reward returned at collision
        """

        self.x, self.y, self.z, self.w, self.h, self.d, self.rx, self.ry, self.rz = components
        self._make_block(*components)
        self.texture = texture
        self._compatible_types = ('robot', 'brick')
        if not block_type in self._compatible_types:
            raise Exception("Uncompatible block type : "+block_type)
        self.block_type = block_type
        self.visible = visible
        self.isGhost = ghost
        # return reward when collided
        self.collision_reward=collision_reward

    @property
    def components(self):
        return self.x, self.y, self.z, self.w, self.h, self.d, self.rx, self.ry, self.rz

    @property
    def position(self):
        return (self.x, self.y, self.z)

    @position.setter
    def position(self,position):
        self.x, self.y, self.z = position

    @property
    def vertices(self):
        """ Return vertices as python list of coordinates
        """
        return self._vertices.flatten().tolist()[0]
    
    def _make_block(self, x_off, y_off, z_off, w, h, d, rx=0, ry=0, rz=0):
        """ Return a np array of the vertices of the cube at position x_off, y_off, z_off
            with size w d h and rotation rx ry rz around x y z axis.
            Note : y axis is up-down, (x,z) is the ground plane
        """
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        # first create a block centered around (0,0,0)
        self._vertices = self.block_vertices(w,h,d)
        # then rotate it along x, y, z axis
        self.rotate(rx,ry,rz)
        # finally translate it of x_off, y_off, z_off
        self.translateTo(x_off,y_off,z_off)

    @staticmethod
    def block_vertices(w, h, d):
        """ Return a np array of the vertices of the block centered on origin with no rotation,
            and with size w d h
            Note : y axis is up-down, (x,z) is the ground plane
        """
        w2=w/2.0; h2=h/2.0; d2=d/2.0
        return np.array([
            [0.0-w2,0.0+h2,0.0-d2],[0.0-w2,0.0+h2,0.0+d2],[0.0+w2,0.0+h2,0.0+d2],[0.0+w2,0.0+h2,0.0-d2],  # top
            [0.0-w2,0.0-h2,0.0-d2],[0.0+w2,0.0-h2,0.0-d2],[0.0+w2,0.0-h2,0.0+d2],[0.0-w2,0.0-h2,0.0+d2],  # bottom
            [0.0-w2,0.0-h2,0.0-d2],[0.0-w2,0.0-h2,0.0+d2],[0.0-w2,0.0+h2,0.0+d2],[0.0-w2,0.0+h2,0.0-d2],  # left
            [0.0+w2,0.0-h2,0.0+d2],[0.0+w2,0.0-h2,0.0-d2],[0.0+w2,0.0+h2,0.0-d2],[0.0+w2,0.0+h2,0.0+d2],  # right
            [0.0-w2,0.0-h2,0.0+d2],[0.0+w2,0.0-h2,0.0+d2],[0.0+w2,0.0+h2,0.0+d2],[0.0-w2,0.0+h2,0.0+d2],  # front
            [0.0+w2,0.0-h2,0.0-d2],[0.0-w2,0.0-h2,0.0-d2],[0.0-w2,0.0+h2,0.0-d2],[0.0+w2,0.0+h2,0.0-d2]   # back
            ])

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
    
    def translate(self,dx,dy,dz):
        """Translates vertices of offset vector
        """
        self._vertices += np.array([dx,dy,dz])
        self.x += dx
        self.y += dy
        self.z += dz

    def translateTo(self,x,y,z):
        """Translates all vertices to center them on x,y,z
        """
        self.translate(x-self.x,y-self.y,z-self.z)
        self.x = x
        self.y = y
        self.z = z

    def rotate(self,rx,ry,rz):
        """Rotate vertices around x, y, z axis
            WARNING : block must be centered around origin, if not rx,ry and rz will become wrong values
        """
        Rx,Ry,Rz = rotation_matrices(rx,ry,rz)        
        R = np.matmul( Rx, np.matmul(Ry,Rz) )
        self._vertices = np.transpose(  np.dot(R, np.transpose(self._vertices))  )
        self.rx += rx
        self.ry += ry
        self.rz += rz    

    def translate_and_rotate_to(self,x_off, y_off, z_off, rx, ry, rz):
        """
        Translate and rotate to given values (absolute and not relative transforms)
        """
        self._make_block(x_off, y_off, z_off, self.w, self.h, self.d, rx, ry, rz)
        self.x, self.y, self.z = x_off, y_off, z_off
        




class Cube(Block):

    def __init__(self,components,texture,block_type):

        x,y,z,w,rx,ry,rz = components
        super(Cube,self).__init__( (x,y,z,w,w,w,rx,ry,rz),texture,block_type)

    def cube_vertices(x_off, y_off, z_off, w, rx=0, ry=0, rz=0):
        """ Return the vertices of the cube at position x, y, z with size w.
            y is up
        """        
        return self.block_vertices(x_off, y_off, z_off, w, w, w, rx, ry, rz) 




class Model(object):

    def __init__(self, world="rb1", show_robot = False):

        # reference to window
        self.window = None
        
        # A set of all blocks
        self.bricks = set()
        
        # Mapping from shown blocks to their texture
        self.shown = dict()

        # wether to show robot or not
        self.show_robot = show_robot       

        self.ticks_per_sec = 60

        self.walking_speed = 10
        self.initial_walking = 10
        self.flying_speed = 15
        
        self.world_info = None
        self.texture_paths = None # used for rendering with window
        self.start_position, self.start_rotation, self.start_strafe = None,None,None
        self.robot_height, self.robot_diameter = None,None

        # load world        
        self.load_world(world)

        self.flying, self.collided, self.current_reward = None, None, None

        # reset first time
        self.reset()
        
    def reset(self):
        # Current x, y, z position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.robot_position = self.start_position

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.robot_rotation = self.start_rotation

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
        block = Block( components, texture, block_type, visible, ghost, collision_reward )
        if block_type=='brick':
            self.bricks.add( block )
        else:
            self.robot_block = block 


    def remove_block(self, block):
        """ Remove the block
        """        
        if block in self.shown:
            self.hide_block(block)
            
        if not block==self.robot_block:
            self.bricks.remove(block)
        else:
            del self.robot_block
        
   
    def show_block(self, block):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        block id
            The (x, y, z) position of the block to show.        
        """
        #self.shown[block] = block.texture
        if block.visible:   
            self.window.show_block(block)

    def show_all_bricks(self):
        """ Show all blocks at once
        """
        for block in self.bricks:
            if block.block_type=='brick' and block.visible:
                self.show_block(block)
    

    def hide_block(self, block):
        """ Hide the block . Hiding does not remove the
        block from the world.
        """
        self.shown.pop(block)
        

    # def get_sight_vector(self):
    #     """ Returns the current line of sight vector indicating the direction
    #     the player is looking.
    #     """
    
    #     x, y = self.robot_rotation
    #     # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
    #     # is 1 when looking ahead parallel to the ground and 0 when looking
    #     # straight up or down.
    #     m = math.cos(math.radians(y))
    #     # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
    #     # looking straight up.
    #     dy = math.sin(math.radians(y))
    #     dx = math.cos(math.radians(x - 90)) * m
    #     dz = math.sin(math.radians(x - 90)) * m
    #     return (dx, dy, dz)

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
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
        x,y = (x+dx +180)%360 -180, (y+dy +180)%360 -180
        self.robot_rotation = [ x, y ]

    def update(self, dt):
        """ This is where mostof the motion logic lives

        Parameters
        ----------
        dt : float
            The change in time since the last call.
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

        if self.show_robot:
            # update robot's block            
            rx,ry = self.robot_rotation
            x, y, z = self.robot_position
            self.robot_block.translate_and_rotate_to(x,y,z,-ry,-rx,0.0)
            # try: # if robot is shown, update the shown vertices
            self.shown[self.robot_block].vertices = self.robot_block.vertices
            # except:
            #     None


    def collide(self, new_position):
        """ Checks to see if the cylindric robot at the given new x,y,z
        position with given diamter and height
        is colliding with any blocks in the world.

        Parameter
        --------
        new_position : new position of robot to check

        Returns
        -------
        Bool : collided
        """
        
        # iterate over blocks and check for collision :
        # TODO : improve collision result for sliding on walls
        # TODO : improve to integer diagonal walls
        # TODO : optimize with walls and floors (x2) or with quadtree
        x,y,z = new_position
        self.current_reward=0.0
        robot_width = self.robot_block.w
        robot_height = self.robot_block.h
        for brick in self.bricks:
            xcol,ycol,zcol = False,False,False
            xb,yb,zb,w,h,d,_,_,_ = brick.components
            if abs(x-xb) <  (w+robot_width)/2.0:
                xcol = True
            if abs(z-zb) <  (d+robot_width)/2.0:
                zcol = True
            if abs(y-yb) <  (h+robot_height)/2.0 :
                ycol = True
            if xcol and zcol and ycol:
                # get block collision reward to be used in RL envs, then return True
                self.current_reward += brick.collision_reward
                if not brick.isGhost: # detect collision only if block is not ghost
                    return True           

        return False


    def load_world(self, world):
        """ Loads the world passed as string parameter

        """
        if world == 'rb1':
            texture_paths, world_info = round_bot_worlds.build_rb1_world(self)
        elif world == 'rb1_blocks':
            texture_paths, world_info = round_bot_worlds.build_rb1_blocks_world(self)
        else:
            raise(Exception('Error: unknown world : ' + world))

        self.world_info = world_info
        self.texture_paths = texture_paths
        self.start_position = self.robot_block.position
        # Note: ry,rx -> x,y cause x is (Oxz) wheras rx is rotation around x, same for y and ry
        self.start_rotation = (self.robot_block.ry, self.robot_block.rx)
        self.start_strafe = [0.0,0.0] # start with a null strafe
            


