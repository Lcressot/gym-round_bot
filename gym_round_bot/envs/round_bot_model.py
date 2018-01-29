
import random
import time
import math
import round_bot_worlds


"""
    This file defines the environnement's Model
"""

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.
        y is up
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]


def block_vertices(x, y, z, w, h, d):
    """ Return the vertices of the cube at position x, y, z with size w d h.
        y is up
    """
    w2=w/2.0; h2=h/2.0; d2=d/2.0
    return [
        x-w2,y+h2,z-d2, x-w2,y+h2,z+d2, x+w2,y+h2,z+d2, x+w2,y+h2,z-d2,  # top
        x-w2,y-h2,z-d2, x+w2,y-h2,z-d2, x+w2,y-h2,z+d2, x-w2,y-h2,z+d2,  # bottom
        x-w2,y-h2,z-d2, x-w2,y-h2,z+d2, x-w2,y+h2,z+d2, x-w2,y+h2,z-d2,  # left
        x+w2,y-h2,z+d2, x+w2,y-h2,z-d2, x+w2,y+h2,z-d2, x+w2,y+h2,z+d2,  # right
        x-w2,y-h2,z+d2, x+w2,y-h2,z+d2, x+w2,y+h2,z+d2, x-w2,y+h2,z+d2,  # front
        x+w2,y-h2,z-d2, x-w2,y-h2,z-d2, x-w2,y+h2,z-d2, x+w2,y+h2,z-d2,  # back
    ]

def center_block(vertices):
    """ Returns the center of the block. Compute the middle of a diagonal
        
    """
    # offset of diagonal point of first point
    ofs = 36
    return [ (vertices[0]+vertices[0+ofs])/2.0, (vertices[1]+vertices[1+ofs])/2.0, (vertices[2]+vertices[2+ofs])/2.0 ]


def tex_coord(x, y, n=4):
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


class Model(object):

    def __init__(self, world="tc1"):

        # reference to window
        self.window = None

        # A number to keep trace of te number of created blocks
        self.num_blocks_added = 0

        # A set of the current block ids
        self.block_ids = set()

        # A mapping from blocks id to the block components x,y,z,w,h,d
        self.blocks = {}

        # A mapping from blocks id to the blocks vertices
        self.block_vertices = {}

        # A mapping from block id to the texture of the block at that block id.
        # This defines all the blocks that are currently in the world.
        self.textures = {}

        # Same mapping as `textures` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from block id to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of block ids inside that sector.
        #self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        #self.queue = deque()

        self.reset()

        self.ticks_per_sec = 60

        self.robot_height = 1
        self.robot_diameter = 0.5

        self.walking_speed = 10
        self.flying_speed = 15

        self.texture_path = None # used for rendering with window
        # load world        
        self.load_world(world)
        
    def reset(self):
        # Current x, y, z position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.robot_position = [0, 1.2, 0]

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.robot_rotation = [0, 0]


        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        self.flying = False   
        self.collided = False     

    def add_block(self, components, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        components : list of x,y,z,w,h,d block components
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        self.num_blocks_added = self.num_blocks_added+1
        new_block_id = self.num_blocks_added
        self.block_ids.add(new_block_id)
        self.blocks[new_block_id] =  components
        self.block_vertices[new_block_id] = block_vertices(*components)
        self.textures[new_block_id] = texture
        #self.sectors.setdefault(sectorize(center_position), []).append(center_position)
        if immediate:
            #if self.exposed(position):
            self.show_block(new_block_id)
            #self.check_neighbors(position)

    def remove_block(self, block_id, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        vertices = self.textures[block_id]
        center_position = center_block(vertices)
        #self.sectors[sectorize(center_position)].remove(center_position)
        if immediate:
            if block_id in self.shown:
                self.hide_block(block_id)
            #self.check_neighbors(position)
        del self.textures[block_id]
        del self.blocks[block_id]
        del self.block_vertices[block_id]
        del self.block_ids[block_id]

   
    def show_block(self, block_id, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        block id
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.textures[block_id]
        self.shown[block_id] = texture
        if immediate:
            self.window.show_block(block_id, texture)
        else:
            self._enqueue(self._show_block, block_id, texture)

    def show_all_blocks(self):
        """ Show all blocks at once
        """
        for block_id in self.block_ids:
            self.show_block(block_id)
    

    def hide_block(self, block_id, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        block_id : id of the block
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(block_id)
        if immediate:
            self._hide_block(block_id)
        else:
            self._enqueue(self._hide_block, block_id)

    def _hide_block(self, block_id):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(block_id).delete()

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.robot_rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

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
        """ This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = self.flying_speed if self.flying else self.walking_speed
        
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        # if not self.flying:
        #     # Update your vertical speed: if you are falling, speed up until you
        #     # hit terminal velocity; if you are jumping, slow down until you
        #     # start falling.
        #     self.dy -= dt * GRAVITY
        #     self.dy = max(self.dy, -TERMINAL_VELOCITY)
        # dy += self.dy * dt

        # collisions
        x, y, z = self.robot_position
        self.robot_position = self.collide((x,y,z),(x + dx, y + dy, z + dz))
        self.collided = (self.robot_position == (x,y,z))

    def collide(self, cur_position, new_position):
        """ Checks to see if the cylindric robot at the given x,y,z
        position with given diamter and height
        is colliding with any blocks in the world.

        Parameter
        --------
        cur_position : current position of the robot
        new_position : new position of robot to check

        Returns
        -------
        position : tuple of len 3
            The new position of the robot taking into account collisions.

        """
        
        # iterate over blocks and check for collision :
        # TODO : improve collision result for sliding on walls
        # TODO : improve to integer diagonal walls
        # TODO : optimize with walls and floors (x2) or with quadtree
        x,y,z = new_position
        robot_diameter = self.robot_diameter
        robot_height = self.robot_height
        for block_id, block in self.blocks.iteritems():
            xcol,ycol,zcol = False,False,False
            xb,yb,zb,w,h,d = block
            if abs(x-xb) <  w/2.0 + robot_diameter:
                xcol = True
            if abs(z-zb) <  d/2.0 + robot_diameter:
                zcol = True
            if abs(y-robot_height/2.0-yb) <  h/2.0 :
                ycol = True
            if xcol and zcol and ycol:
                return cur_position            

        return list(new_position)


    def load_world(self, world):
        """ Loads the world passed as string parameter

        """
        if world == 'rb1':
            self.texture_path, self.world_info = round_bot_worlds.build_rb1_world(self)
        else:
            raise(Exception('Error: unknown world : ' + world))

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / self.ticks_per_sec:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()

